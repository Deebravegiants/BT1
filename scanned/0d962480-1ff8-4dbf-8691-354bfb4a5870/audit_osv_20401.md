# [H] CVE-2021-3345

## Summary
Severity: High
Advisory: CVE-2021-3345
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-01-29
Source: https://osv.dev/vulnerability/CVE-2021-3345
Type: osv

## Details
_gcry_md_block_write in cipher/hash-common.c in Libgcrypt version 1.9.0 has a heap-based buffer overflow when the digest final function sets a large count value. It is recommended to upgrade to 1.9.1 or later.

## References
- https://git.gnupg.org/cgi-bin/gitweb.cgi?p=libgcrypt.git%3Ba=commit%3Bh=512c0c75276949f13b6373b5c04f7065af750b08
- https://gnupg.org
- https://lists.gnupg.org/pipermail/gnupg-announce/2021q1/000455.html
- https://www.oracle.com//security-alerts/cpujul2021.html
- https://bugs.gentoo.org/show_bug.cgi?id=767814
- https://lists.gnupg.org/pipermail/gnupg-announce/2021q1/000456.html
