# [H] ALPINE-CVE-2018-10887

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-10887
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.8, Alpine:v3.9
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2018-07-10
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-10887
Type: osv

## Affected
- Alpine:v3.10: `libgit2` — affected >=0 <0.27.3-r0
- Alpine:v3.11: `libgit2` — affected >=0 <0.27.3-r0
- Alpine:v3.8: `libgit2` — affected >=0 <0.27.3-r0
- Alpine:v3.9: `libgit2` — affected >=0 <0.27.3-r0

## Details
A flaw was found in libgit2 before version 0.27.3. It has been discovered that an unexpected sign extension in git_delta_apply function in delta.c file may lead to an integer overflow which in turn leads to an out of bound read, allowing to read before the base object. An attacker may use this flaw to leak memory addresses or cause a Denial of Service.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-10887
