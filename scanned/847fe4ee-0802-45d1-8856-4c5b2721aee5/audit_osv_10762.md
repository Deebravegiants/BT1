# [M] CVE-2017-20240

## Summary
Severity: Medium
Advisory: CVE-2017-20240
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-06-12
Source: https://osv.dev/vulnerability/CVE-2017-20240
Type: osv

## Details
Crypt::PBKDF2 versions before 0.261630 for Perl are vulnerable to timing attacks.

These versions use Perl's built-in eq comparison. Discrepancies in timing could be used to guess the underlying derived-key.

## References
- http://www.openwall.com/lists/oss-security/2026/06/12/3
- https://metacpan.org/release/ARODLAND/Crypt-PBKDF2-0.161520/source/lib/Crypt/PBKDF2.pm#L123-148
- https://metacpan.org/release/ARODLAND/Crypt-PBKDF2-0.261630/changes
- https://github.com/arodland/Crypt-PBKDF2/pull/6
