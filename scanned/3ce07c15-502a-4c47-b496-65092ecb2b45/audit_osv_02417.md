# [H] ALPINE-CVE-2022-21824

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-21824
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2022-02-24
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-21824
Type: osv

## Affected
- Alpine:v3.12: `nodejs` — affected >=0 <12.22.10-r0
- Alpine:v3.13: `nodejs` — affected >=0 <14.19.0-r0
- Alpine:v3.14: `nodejs` — affected >=0 <14.19.0-r0
- Alpine:v3.15: `nodejs` — affected >=0 <16.13.2-r0
- Alpine:v3.16: `nodejs` — affected >=0 <16.13.2-r0
- Alpine:v3.17: `nodejs` — affected >=0 <16.13.2-r0
- Alpine:v3.18: `nodejs` — affected >=0 <16.13.2-r0
- Alpine:v3.19: `nodejs` — affected >=0 <16.13.2-r0
- Alpine:v3.20: `nodejs` — affected >=0 <16.13.2-r0
- Alpine:v3.21: `nodejs` — affected >=0 <16.13.2-r0
- Alpine:v3.22: `nodejs` — affected >=0 <16.13.2-r0
- Alpine:v3.23: `nodejs` — affected >=0 <16.13.2-r0
- Alpine:v3.24: `nodejs` — affected >=0 <16.13.2-r0

## Details
Due to the formatting logic of the "console.table()" function it was not safe to allow user controlled input to be passed to the "properties" parameter while simultaneously passing a plain object with at least one property as the first parameter, which could be "__proto__". The prototype pollution has very limited control, in that it only allows an empty string to be assigned to numerical keys of the object prototype.Node.js >= 12.22.9, >= 14.18.3, >= 16.13.2, and >= 17.3.1 use a null protoype for the object these properties are being assigned to.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-21824
