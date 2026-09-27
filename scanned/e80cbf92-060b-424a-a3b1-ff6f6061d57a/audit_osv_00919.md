# [H] ALPINE-CVE-2018-11235

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-11235
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-05-30
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-11235
Type: osv

## Affected
- Alpine:v3.10: `git` — affected >=2.14.0 <2.17.1-r0
- Alpine:v3.11: `git` — affected >=2.14.0 <2.17.1-r0
- Alpine:v3.12: `git` — affected >=2.14.0 <2.17.1-r0
- Alpine:v3.13: `git` — affected >=2.14.0 <2.17.1-r0
- Alpine:v3.14: `git` — affected >=2.14.0 <2.17.1-r0
- Alpine:v3.15: `git` — affected >=2.14.0 <2.17.1-r0
- Alpine:v3.16: `git` — affected >=2.14.0 <2.17.1-r0
- Alpine:v3.17: `git` — affected >=2.14.0 <2.17.1-r0
- Alpine:v3.18: `git` — affected >=2.14.0 <2.17.1-r0
- Alpine:v3.19: `git` — affected >=2.14.0 <2.17.1-r0
- Alpine:v3.20: `git` — affected >=2.14.0 <2.17.1-r0
- Alpine:v3.21: `git` — affected >=2.14.0 <2.17.1-r0
- Alpine:v3.22: `git` — affected >=2.14.0 <2.17.1-r0
- Alpine:v3.23: `git` — affected >=2.14.0 <2.17.1-r0
- Alpine:v3.24: `git` — affected >=2.14.0 <2.17.1-r0
- Alpine:v3.5: `git` — affected >=2.14.0 <2.11.3-r1
- Alpine:v3.6: `git` — affected >=2.14.0 <2.13.7
- Alpine:v3.7: `git` — affected >=2.14.0 <2.15.2-r0
- Alpine:v3.8: `git` — affected >=2.14.0 <2.17.1-r0
- Alpine:v3.9: `git` — affected >=2.14.0 <2.17.1-r0

## Details
In Git before 2.13.7, 2.14.x before 2.14.4, 2.15.x before 2.15.2, 2.16.x before 2.16.4, and 2.17.x before 2.17.1, remote code execution can occur. With a crafted .gitmodules file, a malicious project can execute an arbitrary script on a machine that runs "git clone --recurse-submodules" because submodule "names" are obtained from this file, and then appended to $GIT_DIR/modules, leading to directory traversal with "../" in a name. Finally, post-checkout hooks from a submodule are executed, bypassing the intended design in which hooks are not obtained from a remote server.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-11235
