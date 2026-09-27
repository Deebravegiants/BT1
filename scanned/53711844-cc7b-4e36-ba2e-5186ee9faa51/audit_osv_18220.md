# [H] CVE-2020-25125

## Summary
Severity: High
Advisory: CVE-2020-25125
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-09-03
Source: https://osv.dev/vulnerability/CVE-2020-25125
Type: osv

## Details
GnuPG 2.2.21 and 2.2.22 (and Gpg4win 3.1.12) has an array overflow, leading to a crash or possibly unspecified other impact, when a victim imports an attacker's OpenPGP key, and this key has AEAD preferences. The overflow is caused by a g10/key-check.c error. NOTE: GnuPG 2.3.x is unaffected. GnuPG 2.2.23 is a fixed version.

## References
- http://www.openwall.com/lists/oss-security/2020/09/03/4
- http://www.openwall.com/lists/oss-security/2020/09/03/5
- https://lists.gnupg.org/pipermail/gnupg-announce/2020q3/000448.html
- https://bugzilla.opensuse.org/show_bug.cgi?id=1176034
- https://dev.gnupg.org/rG8ec9573e57866dda5efb4677d4454161517484bc
- https://dev.gnupg.org/T5050
