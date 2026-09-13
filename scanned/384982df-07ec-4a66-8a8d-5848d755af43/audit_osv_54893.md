# [M] CVE-2024-58036

## Summary
Severity: Medium
Advisory: CVE-2024-58036
CVSS: 5.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:L)
Published: 2025-04-05
Source: https://osv.dev/vulnerability/CVE-2024-58036
Type: osv

## Details
Net::Dropbox::API 1.9 and earlier for Perl uses the rand() function as the default source of entropy, which is not cryptographically secure, for cryptographic functions.

Specifically Net::Dropbox::API uses the Data::Random library which specifically states that it is "Useful mostly for test programs". Data::Random uses the rand() function.

## References
- https://security.metacpan.org/docs/guides/random-data-for-security.html
- https://metacpan.org/release/BAREFOOT/Data-Random-0.13/source/lib/Data/Random.pm#L537
- https://metacpan.org/release/NORBU/Net-Dropbox-API-1.9/source/lib/Net/Dropbox/API.pm#L11
- https://metacpan.org/release/NORBU/Net-Dropbox-API-1.9/source/lib/Net/Dropbox/API.pm#L385
- https://perldoc.perl.org/functions/rand
