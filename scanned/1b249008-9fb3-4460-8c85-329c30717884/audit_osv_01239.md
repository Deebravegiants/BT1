# [M] ALPINE-CVE-2018-7159

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-7159
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.8, Alpine:v3.9
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2018-05-17
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-7159
Type: osv

## Affected
- Alpine:v3.10: `nodejs` — affected >=0 <8.11.0-r0
- Alpine:v3.11: `nodejs` — affected >=0 <8.11.0-r0
- Alpine:v3.12: `nodejs` — affected >=0 <8.11.0-r0
- Alpine:v3.13: `nodejs` — affected >=0 <8.11.0-r0
- Alpine:v3.14: `nodejs` — affected >=0 <8.11.0-r0
- Alpine:v3.15: `nodejs` — affected >=0 <8.11.0-r0
- Alpine:v3.16: `nodejs` — affected >=0 <8.11.0-r0
- Alpine:v3.17: `nodejs` — affected >=0 <8.11.0-r0
- Alpine:v3.18: `nodejs` — affected >=0 <8.11.0-r0
- Alpine:v3.19: `nodejs` — affected >=0 <8.11.0-r0
- Alpine:v3.20: `nodejs` — affected >=0 <8.11.0-r0
- Alpine:v3.21: `nodejs` — affected >=0 <8.11.0-r0
- Alpine:v3.22: `nodejs` — affected >=0 <8.11.0-r0
- Alpine:v3.23: `nodejs` — affected >=0 <8.11.0-r0
- Alpine:v3.24: `nodejs` — affected >=0 <8.11.0-r0
- Alpine:v3.8: `nodejs` — affected >=0 <8.11.0-r0
- Alpine:v3.9: `nodejs` — affected >=0 <8.11.0-r0

## Details
The HTTP parser in all current versions of Node.js ignores spaces in the `Content-Length` header, allowing input such as `Content-Length: 1 2` to be interpreted as having a value of `12`. The HTTP specification does not allow for spaces in the `Content-Length` value and the Node.js HTTP parser has been brought into line on this particular difference. The security risk of this flaw to Node.js users is considered to be VERY LOW as it is difficult, and may be impossible, to craft an attack that makes use of this flaw in a way that could not already be achieved by supplying an incorrect value for `Content-Length`. Vulnerabilities may exist in user-code that make incorrect assumptions about the potential accuracy of this value compared to the actual length of the data supplied. Node.js users crafting lower-level HTTP utilities are advised to re-check the length of any input supplied after parsing is complete.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-7159
