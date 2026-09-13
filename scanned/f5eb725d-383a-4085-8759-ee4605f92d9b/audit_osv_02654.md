# [H] ALPINE-CVE-2022-41860

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-41860
Ecosystem: Alpine:v3.15, Alpine:v3.16
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-01-17
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-41860
Type: osv

## Affected
- Alpine:v3.15: `freeradius` — affected >=0.9.3 <3.0.26-r0
- Alpine:v3.16: `freeradius` — affected >=0.9.3 <3.0.26-r0

## Details
In freeradius, when an EAP-SIM supplicant sends an unknown SIM option, the server will try to look that option up in the internal dictionaries. This lookup will fail, but the SIM code will not check for that failure. Instead, it will dereference a NULL pointer, and cause the server to crash.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-41860
