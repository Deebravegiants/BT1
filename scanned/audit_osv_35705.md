# [M] GD::SecurityImage versions through 1.75 for Perl use rand to generate secrets

## Summary
Severity: Medium
Advisory: CVE-2026-13082
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2026-07-17
Source: https://osv.dev/vulnerability/CVE-2026-13082
Type: osv

## Details
GD::SecurityImage versions through 1.75 for Perl use rand to generate secrets.

The random method creates the challenge text used for the CAPTCHA by sampling characters from an array using Perl's built-in rand function, and generates a (by default) six-character string.

The built-in rand function is unsuitable for security applications because it is predictable and reversible.

## References
- https://cpan.org/modules
- https://www.cve.org/CVERecord?id=CVE-2025-40916
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/13xxx/CVE-2026-13082.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-13082
- https://security.metacpan.org/patches/G/GD-SecurityImage/1.75/CVE-2026-13082-r1.patch
- https://github.com/burak/CPAN-GD-SecurityImage
