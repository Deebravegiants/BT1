# [H] ALPINE-CVE-2022-39260

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-39260
Ecosystem: Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-10-19
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-39260
Type: osv

## Affected
- Alpine:v3.13: `git` — affected >=2.31.0 <2.30.6-r0
- Alpine:v3.14: `git` — affected >=2.31.0 <2.32.4-r0
- Alpine:v3.15: `git` — affected >=2.31.0 <2.34.5-r0
- Alpine:v3.16: `git` — affected >=2.31.0 <2.36.3-r0
- Alpine:v3.17: `git` — affected >=2.31.0 <2.38.1-r0
- Alpine:v3.18: `git` — affected >=2.31.0 <2.38.1-r0
- Alpine:v3.19: `git` — affected >=2.31.0 <2.38.1-r0
- Alpine:v3.20: `git` — affected >=2.31.0 <2.38.1-r0
- Alpine:v3.21: `git` — affected >=2.31.0 <2.38.1-r0
- Alpine:v3.22: `git` — affected >=2.31.0 <2.38.1-r0
- Alpine:v3.23: `git` — affected >=2.31.0 <2.38.1-r0
- Alpine:v3.24: `git` — affected >=2.31.0 <2.38.1-r0

## Details
Git is an open source, scalable, distributed revision control system. `git shell` is a restricted login shell that can be used to implement Git's push/pull functionality via SSH. In versions prior to 2.30.6, 2.31.5, 2.32.4, 2.33.5, 2.34.5, 2.35.5, 2.36.3, and 2.37.4, the function that splits the command arguments into an array improperly uses an `int` to represent the number of entries in the array, allowing a malicious actor to intentionally overflow the return value, leading to arbitrary heap writes. Because the resulting array is then passed to `execv()`, it is possible to leverage this attack to gain remote code execution on a victim machine. Note that a victim must first allow access to `git shell` as a login shell in order to be vulnerable to this attack. This problem is patched in versions 2.30.6, 2.31.5, 2.32.4, 2.33.5, 2.34.5, 2.35.5, 2.36.3, and 2.37.4 and users are advised to upgrade to the latest version. Disabling `git shell` access via remote logins is a viable short-term workaround.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-39260
