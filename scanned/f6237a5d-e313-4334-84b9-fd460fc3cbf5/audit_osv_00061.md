# [C] ALPINE-CVE-2016-10229

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2016-10229
Ecosystem: Alpine:v3.3
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-04-04
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-10229
Type: osv

## Affected
- Alpine:v3.3: `linux-grsec` — affected >=0 <4.1.39-r0

## Details
udp.c in the Linux kernel before 4.5 allows remote attackers to execute arbitrary code via UDP traffic that triggers an unsafe second checksum calculation during execution of a recv system call with the MSG_PEEK flag.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-10229
