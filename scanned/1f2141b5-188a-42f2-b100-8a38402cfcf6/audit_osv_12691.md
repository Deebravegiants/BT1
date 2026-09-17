# [C] CVE-2018-14360

## Summary
Severity: Critical
Advisory: CVE-2018-14360
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-07-17
Source: https://osv.dev/vulnerability/CVE-2018-14360
Type: osv

## Details
An issue was discovered in NeoMutt before 2018-07-16. nntp_add_group in newsrc.c has a stack-based buffer overflow because of incorrect sscanf usage.

## References
- https://lists.debian.org/debian-lts-announce/2018/08/msg00001.html
- https://neomutt.org/2018/07/16/release
- https://www.debian.org/security/2018/dsa-4277
- https://github.com/neomutt/neomutt/commit/6296f7153f0c9d5e5cd3aaf08f9731e56621bdd3
