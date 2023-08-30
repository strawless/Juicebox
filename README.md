# Juicebox
A simple repository to monitor the electricity usage of the Juicebox L2 charger.  EnelX took away the public JuiceNet API.  The Juicebox sends out a packet over port 8051 to the EnelX Amazon server.  This script sniffs out this packet, decodes it to get the wattage, current, voltage, and even the temperature.  However, in order to accomplish this, you need to modify your iptables to route the packet to your computer that reads the data and acts as the middleman.

```
iptables -t nat -A PREROUTING -s <juicebox_ip> -d 54.161.147.91 -j DNAT --to-destination <computer_ip>
```