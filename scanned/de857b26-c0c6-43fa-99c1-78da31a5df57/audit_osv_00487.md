# [C] ALPINE-CVE-2017-14064

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2017-14064
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-08-31
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-14064
Type: osv

## Affected
- Alpine:v3.10: `ruby` — affected >=0 <2.4.2-r0
- Alpine:v3.11: `ruby` — affected >=0 <2.4.2-r0
- Alpine:v3.12: `ruby` — affected >=0 <2.4.2-r0
- Alpine:v3.13: `ruby` — affected >=0 <2.4.2-r0
- Alpine:v3.14: `ruby` — affected >=0 <2.4.2-r0
- Alpine:v3.15: `ruby` — affected >=0 <2.4.2-r0
- Alpine:v3.16: `ruby` — affected >=0 <2.4.2-r0
- Alpine:v3.17: `ruby` — affected >=0 <2.4.2-r0
- Alpine:v3.18: `ruby` — affected >=0 <2.4.2-r0
- Alpine:v3.19: `ruby` — affected >=0 <2.4.2-r0
- Alpine:v3.20: `ruby` — affected >=0 <2.4.2-r0
- Alpine:v3.21: `ruby` — affected >=0 <2.4.2-r0
- Alpine:v3.22: `ruby` — affected >=0 <2.4.2-r0
- Alpine:v3.23: `ruby` — affected >=0 <2.4.2-r0
- Alpine:v3.24: `ruby` — affected >=0 <2.4.2-r0
- Alpine:v3.3: `ruby` — affected >=0 <2.2.8-r0
- Alpine:v3.4: `ruby` — affected >=0 <2.3.5-r0
- Alpine:v3.5: `ruby` — affected >=0 <2.3.5-r0
- Alpine:v3.6: `ruby` — affected >=0 <2.4.2-r0
- Alpine:v3.7: `ruby` — affected >=0 <2.4.2-r0
- Alpine:v3.8: `ruby` — affected >=0 <2.4.2-r0
- Alpine:v3.9: `ruby` — affected >=0 <2.4.2-r0

## Details
Ruby through 2.2.7, 2.3.x through 2.3.4, and 2.4.x through 2.4.1 can expose arbitrary memory during a JSON.generate call. The issues lies in using strdup in ext/json/ext/generator/generator.c, which will stop after encountering a '\0' byte, returning a pointer to a string of length zero, which is not the length stored in space_len.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-14064
