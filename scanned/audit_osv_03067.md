# [H] ALPINE-CVE-2024-3651

## Summary
Severity: High
Advisory: ALPINE-CVE-2024-3651
Ecosystem: Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-07-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-3651
Type: osv

## Affected
- Alpine:v3.19: `py3-idna` — affected >=0 <3.7-r0
- Alpine:v3.20: `py3-idna` — affected >=0 <3.7-r0
- Alpine:v3.21: `py3-idna` — affected >=0 <3.7-r0
- Alpine:v3.22: `py3-idna` — affected >=0 <3.7-r0
- Alpine:v3.23: `py3-idna` — affected >=0 <3.7-r0
- Alpine:v3.24: `py3-idna` — affected >=0 <3.7-r0

## Details
A vulnerability was identified in the kjd/idna library, specifically within the `idna.encode()` function, affecting version 3.6. The issue arises from the function's handling of crafted input strings, which can lead to quadratic complexity and consequently, a denial of service condition. This vulnerability is triggered by a crafted input that causes the `idna.encode()` function to process the input with considerable computational load, significantly increasing the processing time in a quadratic manner relative to the input size.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-3651
