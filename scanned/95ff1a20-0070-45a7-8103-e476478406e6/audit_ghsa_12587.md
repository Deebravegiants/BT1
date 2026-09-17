# [M] trust-dns vulnerable to Remote Attackers causing Denial-of-Service (packet loops) with crafted DNS packets

## Summary
Severity: Medium
Advisory: GHSA-5fm9-h728-fwpj
Ecosystem: crates.io
Published: 2023-06-06
Source: https://github.com/advisories/GHSA-5fm9-h728-fwpj
Type: github-advisory

## Affected
- crates.io: `trust-dns-server` — affected >=0 <0.22.1
- crates.io: `trust-dns-server` — affected >=0.23.0-alpha.2 <0.23.0-alpha.3

## Details
trust-dns and trust-dns-server are vulnerable to remotely triggered denial-of-service attacks, consuming both network and CPU resources.
DNS messages with the QR=1 bit set are responded to with a `FormErr` response.
This allows creating a traffic loop, in which these `FormErr` responses are sent nonstop between vulnerable servers.

There are two scenarios how this can be exploited: 1) Create a loop between two instances of trust-dns, consuming network resources, or 2) consuming the CPU of a single instance.

With two instances *A* and *B* an attacker sends a DNS query with a spoofed source IP address to *A*.
*A* replies with a `FormErr` to *B*.
Now both servers with ping-pong the message back and forth until by chance the packet is dropped in the network.
Multiple spoofed packets can be sent by the attacker, increasing resource consumption.

A single server can get locked up replying to itself.
Same setup as above, but now *A* sends the reply to itself.
The packet is sent out as fast as the CPU and network stack manage.
This locks up a CPU core.
Multiple packets from the attacker consume multiple CPU cores.

## References
- https://github.com/bluejekyll/trust-dns/pull/1952
- https://github.com/bluejekyll/trust-dns
- https://rustsec.org/advisories/RUSTSEC-2023-0041.html
