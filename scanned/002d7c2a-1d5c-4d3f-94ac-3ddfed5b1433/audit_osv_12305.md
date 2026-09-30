# [H] CVE-2018-11319

## Summary
Severity: High
Advisory: CVE-2018-11319
CVSS: 7.5 (CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-05-20
Source: https://osv.dev/vulnerability/CVE-2018-11319
Type: osv

## Details
Syntastic (aka vim-syntastic) through 3.9.0 does not properly handle searches for configuration files (it searches the current directory up to potentially the root). This improper handling might be exploited for arbitrary code execution via a malicious gcc plugin, if an attacker has write access to a directory that is a parent of the base directory of the project being checked. NOTE: exploitation is more difficult after 3.8.0 because filename prediction may be needed.

## References
- https://lists.debian.org/debian-lts-announce/2018/07/msg00036.html
- https://www.debian.org/security/2018/dsa-4261
- https://bugs.debian.org/894736
- https://github.com/vim-syntastic/syntastic/issues/2170
- https://github.com/vim-syntastic/syntastic/commit/6d7c0b394e001233dd09ec473fbea2002c72632f
