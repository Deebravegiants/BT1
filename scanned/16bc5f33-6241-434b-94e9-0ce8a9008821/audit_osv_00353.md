# [H] ALPINE-CVE-2017-1000050

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-1000050
Ecosystem: Alpine:v3.10, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-07-17
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-1000050
Type: osv

## Affected
- Alpine:v3.10: `jasper` — affected >=0 <2.0.12-r1
- Alpine:v3.3: `jasper` — affected >=0 <1.900.1-r13
- Alpine:v3.4: `jasper` — affected >=0 <1.900.1-r13
- Alpine:v3.5: `jasper` — affected >=0 <1.900.1-r13
- Alpine:v3.6: `jasper` — affected >=0 <2.0.10-r2
- Alpine:v3.7: `jasper` — affected >=0 <2.0.12-r1
- Alpine:v3.8: `jasper` — affected >=0 <2.0.12-r1
- Alpine:v3.9: `jasper` — affected >=0 <2.0.12-r1

## Details
JasPer 2.0.12 is vulnerable to a NULL pointer exception in the function jp2_encode which failed to check to see if the image contained at least one component resulting in a denial-of-service.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-1000050
