# [M] ALPINE-CVE-2025-58364

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-58364
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-58364
Type: osv

## Affected
- Alpine:v3.20: `cups` — affected >=0 <2.4.16-r0
- Alpine:v3.21: `cups` — affected >=0 <2.4.16-r0
- Alpine:v3.22: `cups` — affected >=0 <2.4.16-r0
- Alpine:v3.23: `cups` — affected >=0 <2.4.13-r0
- Alpine:v3.24: `cups` — affected >=0 <2.4.13-r0

## Details
OpenPrinting CUPS is an open source printing system for Linux and other Unix-like operating systems. In versions 2.4.12 and earlier, an unsafe deserialization and validation of printer attributes causes null dereference in the libcups library. This is a remote DoS vulnerability available in local subnet in default configurations. It can cause the cups & cups-browsed to crash, on all the machines in local network who are listening for printers (so by default for all regular linux machines). On systems where the vulnerability CVE-2024-47176 (cups-filters 1.x/cups-browsed 2.x vulnerability) was not fixed, and the firewall on the machine does not reject incoming communication to IPP port, and the machine is set to be available to public internet, attack vector "Network" is possible. The current versions of CUPS and cups-browsed projects have the attack vector "Adjacent" in their default configurations. Version 2.4.13 contains a patch for CVE-2025-58364.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-58364
