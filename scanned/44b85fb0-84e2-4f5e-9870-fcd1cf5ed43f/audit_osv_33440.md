# [H] WWW::OAuth 1.000 and earlier for Perl uses insecure rand() function for cryptographic functions

## Summary
Severity: High
Advisory: CVE-2025-40905
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2026-02-12
Source: https://osv.dev/vulnerability/CVE-2025-40905
Type: osv

## Details
WWW::OAuth 1.000 and earlier for Perl uses the rand() function as the default source of entropy, which is not cryptographically secure, for cryptographic functions.

## References
- http://www.openwall.com/lists/oss-security/2026/02/13/1
- https://cpan.org/modules
- https://metacpan.org/release/DBOOK/WWW-OAuth-1.000/source/lib/WWW/OAuth.pm#L86
- https://perldoc.perl.org/functions/rand
- https://security.metacpan.org/docs/guides/random-data-for-security.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40905.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40905
