import uos
import machine
import utime

recv_buf=""

print()
print("Machine: \t" + uos.uname()[4])
print("MicroPython: \t" + uos.uname()[3])

machine_uart_1 = machine.UART(1, baudrate=115200)
print(machine_uart_1)

def get_rx_data():
    recv=bytes()
    while machine_uart_1.any()>0:
        recv+=machine_uart_1.read(1)
    res=recv.decode('utf-8')
    return res

def connect_wifi(cmd, uart=machine_uart_1, timeout=3000):
    print("CMD:", cmd)
    uart.write(cmd)
    utime.sleep(7.0)
    wait_response(uart, timeout)
    print()

def send_command(cmd, uart=machine_uart_1, timeout=3000):
    print("CMD: " + cmd)
    uart.write(cmd)
    wait_response(uart, timeout)
    print()
    
def wait_response(uart=machine_uart_1, timeout=3000):
    prvMills = utime.ticks_ms()
    resp = b""

    while (utime.ticks_ms()-prvMills)<timeout:
        if uart.any():
            resp = b"".join([resp, uart.read(1)])

    try:
        print("response:", resp.decode())
    except UnicodeError:
        print("response:", resp)
    
send_command('AT\r\n')
send_command('AT+GMR\r\n')
send_command('AT+CIPSERVER=0\r\n')
send_command('AT+RST\r\n')

send_command('AT+RESTORE\r\n')
send_command('AT+CWMODE?\r\n')
send_command('AT+CWMODE=1\r\n')
send_command('AT+CWMODE?\r\n')

#send_command('AT+CWLAP\r\n', timeout=10000) #List available APs
connect_wifi('AT+CWJAP="CLARO_2G4A5A64","yGJGAzKp8G"\r\n', timeout=5000)

send_command('AT+CIFSR\r\n')
utime.sleep(3.0)

send_command('AT+CIPMUX=1\r\n')
utime.sleep(1.0)

send_command('AT+CIPSERVER=1,80\r\n')
utime.sleep(1.0)

print ('Starting connection to ESP8266...')

while True:
    res =""
    res=get_rx_data()
    utime.sleep(2.0)
    
    print ('Waiting For connection...')
    
    if '+IPD' in res:
        id_index = res.find('+IPD')
        print("resp:", res)
        
        connection_id =  res[id_index+5]
        print("connectionId:" + connection_id)
        print ('Conexao de entrada...')
        
        machine_uart_1.write('AT+CIPSEND=' + connection_id + ',200' + '\r\n')
        utime.sleep(1.0)
        
        machine_uart_1.write('HTTP/1.1 200 OK' + '\r\n')
        machine_uart_1.write('Content-Type: text/html'+'\r\n')
        machine_uart_1.write('Connection: close' + '\r\n')
        machine_uart_1.write(''+'\r\n')
        machine_uart_1.write('<!DOCTYPE HTML>' + '\r\n')
        machine_uart_1.write('<html>' + '\r\n')
        machine_uart_1.write('<body><center><h1>Experiencia AIoT</h1></center>' + '\r\n')
        machine_uart_1.write('<center><h2>Tudo sobre IoT</h2></center>' + '\r\n')
        machine_uart_1.write('</body></html>' + '\r\n')
        utime.sleep(4.0)
        
        send_command('AT+CIPCLOSE='+ connection_id + '\r\n') 
        utime.sleep(2.0)
        recv_buf=""
        
        print ('Waiting for new connection...')
