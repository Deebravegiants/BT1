# [M] ALPINE-CVE-2019-13114

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2019-13114
Ecosystem: Alpine:v3.11
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-06-30
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-13114
Type: osv

## Affected
- Alpine:v3.11: `exiv2` — affected >=0 <0.27.2-r0

## Details
http.c in Exiv2 through 0.27.1 allows a malicious http server to cause a denial of service (crash due to a NULL pointer dereference) by returning a crafted response that lacks a space character.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-13114
