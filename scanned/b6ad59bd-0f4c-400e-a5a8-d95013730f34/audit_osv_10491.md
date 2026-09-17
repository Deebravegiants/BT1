# [M] CVE-2017-16359

## Summary
Severity: Medium
Advisory: CVE-2017-16359
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-11-01
Source: https://osv.dev/vulnerability/CVE-2017-16359
Type: osv

## Details
In radare 2.0.1, a pointer wraparound vulnerability exists in store_versioninfo_gnu_verdef() in libr/bin/format/elf/elf.c.

## References
- https://github.com/radare/radare2/commit/62e39f34b2705131a2d08aff0c2e542c6a52cf0e
- https://github.com/radare/radare2/commit/d21e91f075a7a7a8ed23baa5c1bb1fac48313882
- https://github.com/radare/radare2/commit/fbaf24bce7ea4211e4608b3ab6c1b45702cb243d
- https://github.com/radare/radare2/issues/8764
