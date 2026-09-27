# [H] CVE-2025-68973

## Summary
Severity: High
Advisory: CVE-2025-68973
CVSS: 7.8 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:N)
Published: 2025-12-28
Source: https://osv.dev/vulnerability/CVE-2025-68973
Type: osv

## Details
In GnuPG before 2.4.9, armor_filter in g10/armor.c has two increments of an index variable where one is intended, leading to an out-of-bounds write for crafted input. (For ExtendedLTS, 2.2.51 and later are fixed versions.)

## References
- http://www.openwall.com/lists/oss-security/2025/12/29/11
- https://github.com/gpg/gnupg/blob/ff30683418695f5d2cc9e6cf8c9418e09378ebe4/g10/armor.c#L1305-L1306
- https://github.com/gpg/gnupg/compare/gnupg-2.2.50...gnupg-2.2.51
- https://gpg.fail/memcpy
- https://lists.debian.org/debian-lts-announce/2026/01/msg00008.html
- https://media.ccc.de/v/39c3-to-sign-or-not-to-sign-practical-vulnerabilities-i
- https://news.ycombinator.com/item?id=46403200
- https://www.openwall.com/lists/oss-security/2025/12/28/5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68973.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68973
- https://github.com/gpg/gnupg/commit/115d138ba599328005c5321c0ef9f00355838ca9
