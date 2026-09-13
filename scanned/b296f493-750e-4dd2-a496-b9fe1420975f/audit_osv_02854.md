# [M] ALPINE-CVE-2023-38252

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2023-38252
Ecosystem: Alpine:v3.23
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-07-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-38252
Type: osv

## Affected
- Alpine:v3.23: `w3m` — affected >=0 <0.5.3_git20241203-r0

## Details
An out-of-bounds read flaw was found in w3m, in the Strnew_size function in Str.c. This issue may allow an attacker to cause a denial of service through a crafted HTML file.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-38252
