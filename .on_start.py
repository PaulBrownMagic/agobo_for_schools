#! /usr/bin/python3

# File to ensure only one copy runs at a time, .profile can be called twice.
with open('.running','r') as file:
    is_running = list(file)[0].strip() == 'True'
    print(is_running)

if not is_running:
    print("Started")
    with open('.running', 'w') as file:
        file.write('True')
    import RPi.GPIO as GPIO
    from time import sleep
    from subprocess import check_output, call
    GPIO.setmode(GPIO.BCM)
    RED = 4
    GREEN = 17
    GPIO.setup(RED, GPIO.OUT, initial = 1)
    GPIO.setup(GREEN, GPIO.OUT, initial = 0)

    def get_output(command):
        return check_output(command).decode('utf-8').strip()

    def has_ip():
        return len(get_output(["hostname", "-I"])) > 6 

    def has_license():
        return len(get_output(["cat", "/etc/vnc/licensekey"])) > 15

    def vncserver_started():
        if '0.pid' in get_output(["ls", ".vnc"]):
            process_name = get_output(['cat','.vnc/gui:0.pid'])
            ps_name = get_output(['ps', '-p', process_name, '-o', 'comm='])
            if 'vnc' in ps_name.lower():
                return True
        return False

    red, green = False, True

    # Get IP address -- Flash red
    for _ in range(16):
        red = not red
        GPIO.output(RED, red)
        sleep(0.03)
    while not has_ip():
        red = not red
        GPIO.output(RED, red)
        sleep(0.2)

    GPIO.output(RED, 0)
    GPIO.output(GREEN, 1)

    # Assert License -- Flash red/green
    for _ in range(16):
        red = not red
        green = not green
        GPIO.output(RED, red)
        GPIO.output(GREEN, green)
        sleep(0.05)
    while not has_license():
        red = not red
        green = not green
        GPIO.output(RED, red)
        GPIO.output(GREEN, green)
        call(["sudo","vnclicense","-add", "DAHR2-D2DSQ-BQ3A4-74SJV-KU3WA"])
        sleep(0.2)

    GPIO.output(RED, 0)
    GPIO.output(GREEN, 1)

    # Start VNC server -- Flash green
    call(["vncserver",":!"])
    for _ in range(16):
        green = not green
        GPIO.output(GREEN, green)
        sleep(0.05)
    server_running = vncserver_started()
    while not server_running:
        call(["vncserver",":!"])
        green = not green
        GPIO.output(GREEN, green)
        sleep(0.1)
        server_running = vncserver_started()

    GPIO.output(RED, 0)
    GPIO.output(GREEN, 1)

    # Leave Green light on, morse flash last IP element.
    def get_morse():
        ip_last_bin = bin(int(get_output(["hostname", "-I"]).split(".")[-1]))
        morse = list(map(int,list(ip_last_bin)[2:]))
        if len(morse) <= 4:
            while len(morse) < 4:
                morse = [0] + morse
        elif len(morse) < 8:
            while len(morse) < 8:
                morse = [0] + morse
        return morse

    def has_connection():
        log = get_output(['tail', '.vnc/gui:0.log'])
        return 'connected' in log

    sleep(2)
    morse = get_morse()
    connected = False
    dot = 0.3
    dash = dot * 3

    while not connected:
        connected = has_connection()
        sleep(1)
        for signal in morse:
            GPIO.output(RED, True)
            if signal == 0:
                sleep(dot)
            else:
                sleep(dash)
            GPIO.output(RED, False)
            sleep(dot)
    sleep(1)

    # Exit
    GPIO.cleanup()

with open('.running', 'w') as file:
    file.write('False')
