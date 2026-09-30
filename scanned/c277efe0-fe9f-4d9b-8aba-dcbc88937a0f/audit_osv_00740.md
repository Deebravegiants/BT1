# [C] ALPINE-CVE-2017-7555

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2017-7555
Ecosystem: Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-08-17
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-7555
Type: osv

## Affected
- Alpine:v3.3: `augeas` — affected >=0 <1.4.0-r5
- Alpine:v3.4: `augeas` — affected >=0 <1.5.0-r1
- Alpine:v3.5: `augeas` — affected >=0 <1.6.0-r1
- Alpine:v3.6: `augeas` — affected >=0 <1.8.1-r0

## Details
Augeas versions up to and including 1.8.0 are vulnerable to heap-based buffer overflow due to improper handling of escaped strings. Attacker could send crafted strings that would cause the application using augeas to copy past the end of a buffer, leading to a crash or possible code execution.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-7555
