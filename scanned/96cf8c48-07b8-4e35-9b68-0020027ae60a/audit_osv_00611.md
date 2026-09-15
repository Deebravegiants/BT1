# [C] ALPINE-CVE-2017-2885

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2017-2885
Ecosystem: Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-04-24
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-2885
Type: osv

## Affected
- Alpine:v3.3: `libsoup` — affected >=0 <2.52.2-r1
- Alpine:v3.4: `libsoup` — affected >=0 <2.54.1-r1
- Alpine:v3.5: `libsoup` — affected >=0 <2.56.1-r0
- Alpine:v3.6: `libsoup` — affected >=0 <2.58.2-r0
- Alpine:v3.7: `libsoup` — affected >=0 <2.58.2-r0
- Alpine:v3.8: `libsoup` — affected >=0 <2.58.2-r0

## Details
An exploitable stack based buffer overflow vulnerability exists in the GNOME libsoup 2.58. A specially crafted HTTP request can cause a stack overflow resulting in remote code execution. An attacker can send a special HTTP request to the vulnerable server to trigger this vulnerability.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-2885
