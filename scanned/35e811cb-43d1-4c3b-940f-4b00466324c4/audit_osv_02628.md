# [H] ALPINE-CVE-2022-38223

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-38223
Ecosystem: Alpine:v3.23
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-08-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-38223
Type: osv

## Affected
- Alpine:v3.23: `w3m` — affected >=0 <0.5.3_git20241203-r0

## Details
There is an out-of-bounds write in checkType located in etc.c in w3m 0.5.3. It can be triggered by sending a crafted HTML file to the w3m binary. It allows an attacker to cause Denial of Service or possibly have unspecified other impact.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-38223
