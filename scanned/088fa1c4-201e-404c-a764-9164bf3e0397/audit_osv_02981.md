# [M] ALPINE-CVE-2024-12254

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2024-12254
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2024-12-06
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-12254
Type: osv

## Affected
- Alpine:v3.20: `python3` — affected >=0 <3.12.8-r1
- Alpine:v3.21: `python3` — affected >=0 <3.12.8-r1
- Alpine:v3.22: `python3` — affected >=0 <3.12.8-r1
- Alpine:v3.23: `python3` — affected >=0 <3.12.8-r1
- Alpine:v3.24: `python3` — affected >=0 <3.12.8-r1

## Details
Starting in Python 3.12.0, the asyncio._SelectorSocketTransport.writelines()
 method would not "pause" writing and signal to the Protocol to drain 
the buffer to the wire once the write buffer reached the "high-water 
mark". Because of this, Protocols would not periodically drain the write
 buffer potentially leading to memory exhaustion.





This
 vulnerability likely impacts a small number of users, you must be using
 Python 3.12.0 or later, on macOS or Linux, using the asyncio module 
with protocols, and using .writelines() method which had new 
zero-copy-on-write behavior in Python 3.12.0 and later. If not all of 
these factors are true then your usage of Python is unaffected.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-12254
