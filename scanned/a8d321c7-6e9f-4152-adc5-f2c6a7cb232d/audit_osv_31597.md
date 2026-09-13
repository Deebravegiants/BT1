# [C] Crypt::Sodium::XS module versions prior to 0.000042, for Perl, include a vulnerable version of libsodium

## Summary
Severity: Critical
Advisory: CVE-2025-15444
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-01-06
Source: https://osv.dev/vulnerability/CVE-2025-15444
Type: osv

## Details
Crypt::Sodium::XS module versions prior to 0.000042, for Perl, include a vulnerable version of libsodium

libsodium <= 1.0.20 or a version of libsodium released before December 30, 2025 contains a vulnerability documented as CVE-2025-69277  https://www.cve.org/CVERecord?id=CVE-2025-69277 .

The libsodium vulnerability states:

In atypical use cases involving certain custom cryptography or untrusted data to crypto_core_ed25519_is_valid_point, mishandles checks for whether an elliptic curve point is valid because it sometimes allows points that aren't in the main cryptographic group.

0.000042 includes a version of libsodium updated to 1.0.20-stable, released January 3, 2026, which includes a fix for the vulnerability.

## References
- https://00f.net/2025/12/30/libsodium-vulnerability/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/15xxx/CVE-2025-15444.json
- https://metacpan.org/dist/Crypt-Sodium-XS/changes
- https://nvd.nist.gov/vuln/detail/CVE-2025-15444
- https://github.com/jedisct1/libsodium/commit/ad3004ec8731730e93fcfbbc824e67eadc1c1bae
