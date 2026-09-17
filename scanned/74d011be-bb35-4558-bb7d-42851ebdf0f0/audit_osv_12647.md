# [H] CVE-2018-13982

## Summary
Severity: High
Advisory: CVE-2018-13982
Aliases: GHSA-7gfx-wxfh-7rvm
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-09-18
Source: https://osv.dev/vulnerability/CVE-2018-13982
Type: osv

## Details
Smarty_Security::isTrustedResourceDir() in Smarty before 3.1.33 is prone to a path traversal vulnerability due to insufficient template code sanitization. This allows attackers controlling the executed template code to bypass the trusted directory security restriction and read arbitrary files.

## References
- https://lists.debian.org/debian-lts-announce/2021/04/msg00004.html
- https://lists.debian.org/debian-lts-announce/2021/04/msg00014.html
- https://lists.debian.org/debian-lts-announce/2021/10/msg00015.html
- https://github.com/sbaresearch/advisories/tree/public/2018/SBA-ADV-20180420-01_Smarty_Path_Traversal
- https://github.com/smarty-php/smarty/commit/2e081a51b1effddb23f87952959139ac62654d50
- https://github.com/smarty-php/smarty/commit/8d21f38dc35c4cd6b31c2f23fc9b8e5adbc56dfe
- https://github.com/smarty-php/smarty/commit/bcedfd6b58bed4a7366336979ebaa5a240581531
- https://github.com/smarty-php/smarty/commit/c9dbe1d08c081912d02bd851d1d1b6388f6133d1
- https://github.com/smarty-php/smarty/commit/f9ca3c63d1250bb56b2bda609dcc9dd81f0065f8
