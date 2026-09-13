# [M] Crypt::CBC versions between 1.21 and 3.05 for Perl may use insecure rand() function for cryptographic functions

## Summary
Severity: Medium
Advisory: CVE-2025-2814
CVSS: 4.0 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2025-04-12
Source: https://osv.dev/vulnerability/CVE-2025-2814
Type: osv

## Details
Crypt::CBC versions between 1.21 and 3.05 for Perl may use the rand() function as the default source of entropy, which is not cryptographically secure, for cryptographic functions.

This issue affects operating systems where "/dev/urandom'" is unavailable.  In that case, Crypt::CBC will fallback to use the insecure rand() function.

## References
- https://cpan.org/modules
- https://metacpan.org/dist/Crypt-CBC/source/lib/Crypt/CBC.pm#L777
- https://perldoc.perl.org/functions/rand
- https://security.metacpan.org/docs/guides/random-data-for-security.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/2xxx/CVE-2025-2814.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-2814
- https://github.com/lstein/Lib-Crypt-CBC/commit/37111f7cd894bcec46156ba7f40a49c126ebf535.patch
- https://github.com/lstein/Lib-Crypt-CBC
