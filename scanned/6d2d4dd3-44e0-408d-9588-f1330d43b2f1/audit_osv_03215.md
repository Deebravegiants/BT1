# [M] ALPINE-CVE-2025-22150

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-22150
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:N)
Published: 2025-01-21
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-22150
Type: osv

## Affected
- Alpine:v3.21: `nodejs` — affected >=0 <22.13.1-r0
- Alpine:v3.22: `nodejs` — affected >=0 <22.13.1-r0
- Alpine:v3.23: `nodejs` — affected >=0 <22.13.1-r0
- Alpine:v3.24: `nodejs` — affected >=0 <22.13.1-r0

## Details
Undici is an HTTP/1.1 client. Starting in version 4.5.0 and prior to versions 5.28.5, 6.21.1, and 7.2.3, undici uses `Math.random()` to choose the boundary for a multipart/form-data request. It is known that the output of `Math.random()` can be predicted if several of its generated values are known. If there is a mechanism in an app that sends multipart requests to an attacker-controlled website, they can use this to leak the necessary values. Therefore, an attacker can tamper with the requests going to the backend APIs if certain conditions are met. This is fixed in versions 5.28.5, 6.21.1, and 7.2.3. As a workaround, do not issue multipart requests to attacker controlled servers.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-22150
