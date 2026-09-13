# [M] CVE-2024-57868

## Summary
Severity: Medium
Advisory: CVE-2024-57868
CVSS: 5.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:L)
Published: 2025-04-05
Source: https://osv.dev/vulnerability/CVE-2024-57868
Type: osv

## Details
Web::API 2.8 and earlier for Perl uses the rand() function as the default source of entropy, which is not cryptographically secure, for cryptographic functions.

Specifically Web::API uses the Data::Random library which specifically states that it is "Useful mostly for test programs". Data::Random uses the rand() function.

## References
- https://perldoc.perl.org/functions/rand
- https://security.metacpan.org/docs/guides/random-data-for-security.html
- https://metacpan.org/dist/Web-API/source/lib/Web/API.pm#L20
- https://metacpan.org/dist/Web-API/source/lib/Web/API.pm#L348
- https://metacpan.org/release/BAREFOOT/Data-Random-0.13/source/lib/Data/Random.pm#L537
