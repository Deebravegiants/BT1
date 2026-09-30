# [M] Amazon::Credentials versions through 1.2.0 for Perl uses rand to generate encryption keys

## Summary
Severity: Medium
Advisory: CVE-2026-6146
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-05-11
Source: https://osv.dev/vulnerability/CVE-2026-6146
Type: osv

## Details
Amazon::Credentials versions through 1.2.0 for Perl uses rand to generate encryption keys.

Amazon::Credentials stores credentials in an obfuscated form to prevent access to the secrets from a data dump of the object.

Before version 1.3.0, the secrets were encrypted using a 64-bit key that was generated using the built-in rand function, which is predictable and unsuitable for cryptography.

## References
- http://www.openwall.com/lists/oss-security/2026/05/11/15
- https://cpan.org/modules
- https://metacpan.org/release/BIGFOOT/Amazon-Credentials-1.2.0/source/lib/Amazon/Credentials.pm#L1415-1418
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/6xxx/CVE-2026-6146.json
- https://metacpan.org/release/BIGFOOT/Amazon-Credentials-1.3.0/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-6146
- https://github.com/rlauer6/Amazon-Credentials
