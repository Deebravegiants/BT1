# [H] ALPINE-CVE-2016-6301

## Summary
Severity: High
Advisory: ALPINE-CVE-2016-6301
Ecosystem: Alpine:v3.2, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-12-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-6301
Type: osv

## Affected
- Alpine:v3.2: `busybox` — affected >=0 <1.24.2-r1
- Alpine:v3.3: `busybox` — affected >=0 <1.24.2-r1
- Alpine:v3.4: `busybox` — affected >=0 <1.24.2-r12
- Alpine:v3.5: `busybox` — affected >=0 <1.25.0-r0

## Details
The recv_and_process_client_pkt function in networking/ntpd.c in busybox allows remote attackers to cause a denial of service (CPU and bandwidth consumption) via a forged NTP packet, which triggers a communication loop.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-6301
