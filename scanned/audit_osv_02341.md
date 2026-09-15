# [M] ALPINE-CVE-2021-44533

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2021-44533
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2022-02-24
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-44533
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
Node.js < 12.22.9, < 14.18.3, < 16.13.2, and < 17.3.1 did not handle multi-value Relative Distinguished Names correctly. Attackers could craft certificate subjects containing a single-value Relative Distinguished Name that would be interpreted as a multi-value Relative Distinguished Name, for example, in order to inject a Common Name that would allow bypassing the certificate subject verification.Affected versions of Node.js that do not accept multi-value Relative Distinguished Names and are thus not vulnerable to such attacks themselves. However, third-party code that uses node's ambiguous presentation of certificate subjects may be vulnerable.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-44533
