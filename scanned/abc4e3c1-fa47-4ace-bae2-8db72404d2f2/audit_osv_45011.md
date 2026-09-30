# [M] Crypt::PBKDF2 versions before 0.261630 for Perl have a weak default algorithm and number of iterations

## Summary
Severity: Medium
Advisory: CVE-2026-9641
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-06-12
Source: https://osv.dev/vulnerability/CVE-2026-9641
Type: osv

## Details
Crypt::PBKDF2 versions before 0.261630 for Perl have a weak default algorithm and number of iterations.

The default algorithm is HMAC-SHA1, which should only be used for legacy systems.

These versions default to using 1000 iterations.

Depending on the chosen algorithm, 220,000 to 1,400,000 iterations should be used.

## References
- http://www.openwall.com/lists/oss-security/2026/06/12/5
- http://www.openwall.com/lists/oss-security/2026/06/13/1
- http://www.openwall.com/lists/oss-security/2026/06/14/1
- http://www.openwall.com/lists/oss-security/2026/06/14/2
- http://www.openwall.com/lists/oss-security/2026/06/14/3
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/9xxx/CVE-2026-9641.json
- https://metacpan.org/release/ARODLAND/Crypt-PBKDF2-0.261630/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-9641
- https://github.com/arodland/Crypt-PBKDF2
- https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html#pbkdf2
