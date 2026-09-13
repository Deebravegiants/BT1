# [M] Amon2::Auth::Site::LINE versions through 0.04 for Perl uses insecure rand() function for cryptographic functions

## Summary
Severity: Medium
Advisory: CVE-2024-57835
CVSS: 5.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:L)
Published: 2025-04-05
Source: https://osv.dev/vulnerability/CVE-2024-57835
Type: osv

## Details
Amon2::Auth::Site::LINE uses the String::Random module to generate nonce values. 

String::Random defaults to Perl's built-in predictable random number generator, the rand() function, which is not cryptographically secure

## References
- https://cpan.org/modules
- https://metacpan.org/release/SHLOMIF/String-Random-0.32/source/lib/String/Random.pm#L377
- https://metacpan.org/release/TANIGUCHI/Amon2-Auth-Site-LINE-0.04/source/lib/Amon2/Auth/Site/LINE.pm#L235
- https://metacpan.org/release/TANIGUCHI/Amon2-Auth-Site-LINE-0.04/source/lib/Amon2/Auth/Site/LINE.pm#L255
- https://security.metacpan.org/docs/guides/random-data-for-security.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57835.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57835
- https://github.com/nipotan/p5-Amon2-Auth-Site-LINE
