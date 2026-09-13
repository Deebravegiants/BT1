# [H] ALPINE-CVE-2021-21300

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-21300
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-03-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-21300
Type: osv

## Affected
- Alpine:v3.10: `git` — affected >=2.17.0 <2.22.5-r0
- Alpine:v3.11: `git` — affected >=2.17.0 <2.24.4-r0
- Alpine:v3.12: `git` — affected >=2.17.0 <2.26.3-r0
- Alpine:v3.13: `git` — affected >=2.17.0 <2.30.2-r0
- Alpine:v3.14: `git` — affected >=2.17.0 <2.30.2-r0
- Alpine:v3.15: `git` — affected >=2.17.0 <2.30.2-r0
- Alpine:v3.16: `git` — affected >=2.17.0 <2.30.2-r0
- Alpine:v3.17: `git` — affected >=2.17.0 <2.30.2-r0
- Alpine:v3.18: `git` — affected >=2.17.0 <2.30.2-r0
- Alpine:v3.19: `git` — affected >=2.17.0 <2.30.2-r0
- Alpine:v3.20: `git` — affected >=2.17.0 <2.30.2-r0
- Alpine:v3.21: `git` — affected >=2.17.0 <2.30.2-r0
- Alpine:v3.22: `git` — affected >=2.17.0 <2.30.2-r0
- Alpine:v3.23: `git` — affected >=2.17.0 <2.30.2-r0
- Alpine:v3.24: `git` — affected >=2.17.0 <2.30.2-r0

## Details
Git is an open-source distributed revision control system. In affected versions of Git a specially crafted repository that contains symbolic links as well as files using a clean/smudge filter such as Git LFS, may cause just-checked out script to be executed while cloning onto a case-insensitive file system such as NTFS, HFS+ or APFS (i.e. the default file systems on Windows and macOS). Note that clean/smudge filters have to be configured for that. Git for Windows configures Git LFS by default, and is therefore vulnerable. The problem has been patched in the versions published on Tuesday, March 9th, 2021. As a workaound, if symbolic link support is disabled in Git (e.g. via `git config --global core.symlinks false`), the described attack won't work. Likewise, if no clean/smudge filters such as Git LFS are configured globally (i.e. _before_ cloning), the attack is foiled. As always, it is best to avoid cloning repositories from untrusted sources. The earliest impacted version is 2.14.2. The fix versions are: 2.30.1, 2.29.3, 2.28.1, 2.27.1, 2.26.3, 2.25.5, 2.24.4, 2.23.4, 2.22.5, 2.21.4, 2.20.5, 2.19.6, 2.18.5, 2.17.62.17.6.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-21300
