# [C] ALPINE-CVE-2018-8828

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2018-8828
Ecosystem: Alpine:v3.4, Alpine:v3.5, Alpine:v3.6
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-03-20
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-8828
Type: osv

## Affected
- Alpine:v3.4: `kamailio` — affected >=5.0.0 <4.4.0-r2
- Alpine:v3.5: `kamailio` — affected >=5.0.0 <4.4.5-r1
- Alpine:v3.6: `kamailio` — affected >=5.0.0 <5.0.2-r2

## Details
A Buffer Overflow issue was discovered in Kamailio before 4.4.7, 5.0.x before 5.0.6, and 5.1.x before 5.1.2. A specially crafted REGISTER message with a malformed branch or From tag triggers an off-by-one heap-based buffer overflow in the tmx_check_pretran function in modules/tmx/tmx_pretran.c.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-8828
