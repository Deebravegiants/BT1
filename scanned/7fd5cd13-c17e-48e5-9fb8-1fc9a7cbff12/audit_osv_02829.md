# [M] ALPINE-CVE-2023-32324

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2023-32324
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-06-01
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-32324
Type: osv

## Affected
- Alpine:v3.15: `cups` — affected >=0 <2.3.3-r7
- Alpine:v3.16: `cups` — affected >=0 <2.4.2-r1
- Alpine:v3.17: `cups` — affected >=0 <2.4.2-r2
- Alpine:v3.18: `cups` — affected >=0 <2.4.2-r7
- Alpine:v3.19: `cups` — affected >=0 <2.4.2-r7
- Alpine:v3.20: `cups` — affected >=0 <2.4.2-r7
- Alpine:v3.21: `cups` — affected >=0 <2.4.2-r7
- Alpine:v3.22: `cups` — affected >=0 <2.4.2-r7
- Alpine:v3.23: `cups` — affected >=0 <2.4.2-r7
- Alpine:v3.24: `cups` — affected >=0 <2.4.2-r7

## Details
OpenPrinting CUPS is an open source printing system. In versions 2.4.2 and prior, a heap buffer overflow vulnerability would allow a remote attacker to launch a denial of service (DoS) attack. A buffer overflow vulnerability in the function `format_log_line` could allow remote attackers to cause a DoS on the affected system. Exploitation of the vulnerability can be triggered when the configuration file `cupsd.conf` sets the value of `loglevel `to `DEBUG`. No known patches or workarounds exist at time of publication.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-32324
