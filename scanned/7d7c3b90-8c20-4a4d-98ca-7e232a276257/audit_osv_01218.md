# [M] ALPINE-CVE-2018-6198

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-6198
Ecosystem: Alpine:v3.23
CVSS: 4.7 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-01-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-6198
Type: osv

## Affected
- Alpine:v3.23: `w3m` — affected >=0 <0.5.3_git20241203-r0

## Details
w3m through 0.5.3 does not properly handle temporary files when the ~/.w3m directory is unwritable, which allows a local attacker to craft a symlink attack to overwrite arbitrary files.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-6198
