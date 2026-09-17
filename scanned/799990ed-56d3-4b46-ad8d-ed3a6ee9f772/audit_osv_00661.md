# [H] ALPINE-CVE-2017-5495

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-5495
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-01-24
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-5495
Type: osv

## Affected
- Alpine:v3.10: `quagga` — affected >=0 <1.1.1-r0
- Alpine:v3.11: `quagga` — affected >=0 <1.1.1-r0
- Alpine:v3.12: `quagga` — affected >=0 <1.1.1-r0
- Alpine:v3.13: `quagga` — affected >=0 <1.1.1-r0
- Alpine:v3.14: `quagga` — affected >=0 <1.1.1-r0
- Alpine:v3.15: `quagga` — affected >=0 <1.1.1-r0
- Alpine:v3.16: `quagga` — affected >=0 <1.1.1-r0
- Alpine:v3.17: `quagga` — affected >=0 <1.1.1-r0
- Alpine:v3.18: `quagga` — affected >=0 <1.1.1-r0
- Alpine:v3.19: `quagga` — affected >=0 <1.1.1-r0
- Alpine:v3.20: `quagga` — affected >=0 <1.1.1-r0
- Alpine:v3.21: `quagga` — affected >=0 <1.1.1-r0
- Alpine:v3.22: `quagga` — affected >=0 <1.1.1-r0
- Alpine:v3.23: `quagga` — affected >=0 <1.1.1-r0
- Alpine:v3.24: `quagga` — affected >=0 <1.1.1-r0
- Alpine:v3.5: `quagga` — affected >=0 <1.1.1-r0
- Alpine:v3.6: `quagga` — affected >=0 <1.1.1-r0
- Alpine:v3.7: `quagga` — affected >=0 <1.1.1-r0
- Alpine:v3.8: `quagga` — affected >=0 <1.1.1-r0
- Alpine:v3.9: `quagga` — affected >=0 <1.1.1-r0

## Details
All versions of Quagga, 0.93 through 1.1.0, are vulnerable to an unbounded memory allocation in the telnet 'vty' CLI, leading to a Denial-of-Service of Quagga daemons, or even the entire host. When Quagga daemons are configured with their telnet CLI enabled, anyone who can connect to the TCP ports can trigger this vulnerability, prior to authentication. Most distributions restrict the Quagga telnet interface to local access only by default. The Quagga telnet interface 'vty' input buffer grows automatically, without bound, so long as a newline is not entered. This allows an attacker to cause the Quagga daemon to allocate unbounded memory by sending very long strings without a newline. Eventually the daemon is terminated by the system, or the system itself runs out of memory. This is fixed in Quagga 1.1.1 and Free Range Routing (FRR) Protocol Suite 2017-01-10.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-5495
