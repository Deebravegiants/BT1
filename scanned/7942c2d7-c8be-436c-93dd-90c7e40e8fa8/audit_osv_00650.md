# [H] ALPINE-CVE-2017-5029

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-5029
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.2, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-04-24
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-5029
Type: osv

## Affected
- Alpine:v3.10: `libxslt` — affected >=0 <1.1.29-r1
- Alpine:v3.11: `libxslt` — affected >=0 <1.1.29-r1
- Alpine:v3.12: `libxslt` — affected >=0 <1.1.29-r1
- Alpine:v3.13: `libxslt` — affected >=0 <1.1.29-r1
- Alpine:v3.14: `libxslt` — affected >=0 <1.1.29-r1
- Alpine:v3.15: `libxslt` — affected >=0 <1.1.29-r1
- Alpine:v3.16: `libxslt` — affected >=0 <1.1.29-r1
- Alpine:v3.17: `libxslt` — affected >=0 <1.1.29-r1
- Alpine:v3.18: `libxslt` — affected >=0 <1.1.29-r1
- Alpine:v3.19: `libxslt` — affected >=0 <1.1.29-r1
- Alpine:v3.2: `libxslt` — affected >=0 <1.1.29-r1
- Alpine:v3.20: `libxslt` — affected >=0 <1.1.29-r1
- Alpine:v3.21: `libxslt` — affected >=0 <1.1.29-r1
- Alpine:v3.22: `libxslt` — affected >=0 <1.1.29-r1
- Alpine:v3.23: `libxslt` — affected >=0 <1.1.29-r1
- Alpine:v3.24: `libxslt` — affected >=0 <1.1.29-r1
- Alpine:v3.3: `libxslt` — affected >=0 <1.1.29-r1
- Alpine:v3.4: `libxslt` — affected >=0 <1.1.29-r1
- Alpine:v3.5: `libxslt` — affected >=0 <1.1.29-r1
- Alpine:v3.6: `libxslt` — affected >=0 <1.1.29-r1
- Alpine:v3.7: `libxslt` — affected >=0 <1.1.29-r1
- Alpine:v3.8: `libxslt` — affected >=0 <1.1.29-r1
- Alpine:v3.9: `libxslt` — affected >=0 <1.1.29-r1

## Details
The xsltAddTextString function in transform.c in libxslt 1.1.29, as used in Blink in Google Chrome prior to 57.0.2987.98 for Mac, Windows, and Linux and 57.0.2987.108 for Android, lacked a check for integer overflow during a size calculation, which allowed a remote attacker to perform an out of bounds memory write via a crafted HTML page.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-5029
