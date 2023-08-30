import socket

class Juicebox:
    lookup = {
        'V' : 'voltage',
        'L' : 'lifetime_power',
        'T' : 'temperature',
        'f' : 'frequency',
        'E' : 'session_power',
        'A' : 'current',
        'S' : 'charging'
    }

    def __init__(self, juicebox_ip, callback):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) # UDP

        # Enable Reuse
        # client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Enable broadcasting mode
        #client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        self.client.bind(("", 8051))
        self.callback = callback

        self.juicebox_ip = juicebox_ip


    def readForever(self):
        while True:
            # Receive the Juicebox UDP packet
            data, addr = self.client.recvfrom(1024)
            
            status = {
                'current' : 0,
                'session_power' : 0
            }
            items = data.decode().split(",")
                    
            for item in items:
                if item[0] in self.lookup:
                    s = self.lookup[item[0]]
                    status[s] = item[1::]
                    if s == 'voltage' :
                        status[s] = item[1:4] + "." + item[4:]
                    elif s == 'frequency':
                        status[s] = item[1:3] + "." + item[3:]
                    elif s == 'current':
                        status[s] = item[1:5] + "." + item[5:]

            if 'voltage' in status:
                watts = float(status['current']) * float(status['voltage'])
                self.callback(watts)
            
            
            # send the packet off to the Enel X cloud
            dest_addr = ("54.161.147.91", 8051)
            self.client.sendto(data, dest_addr)
            
            # Wait for the Enel X cloud to send an ACK back
            data, addr = self.client.recvfrom(1024)
            
            # Send the ACK to the juicebox
            dest_addr = (self.juicebox_ip, 8051)
            self.client.sendto(data, dest_addr)
                
def print_updates(watts):
    print("New Wattage Received %f" %(watts))

if __name__ == "__main__":
    try:
        j = Juicebox("192.168.50.202", print_updates)
        j.readForever()
    except KeyboardInterrupt:
        print("Interrupt received.  Stopping")
