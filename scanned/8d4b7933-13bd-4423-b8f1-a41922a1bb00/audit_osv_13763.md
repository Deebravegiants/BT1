# [H] CVE-2018-25107

## Summary
Severity: High
Advisory: CVE-2018-25107
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-12-29
Source: https://osv.dev/vulnerability/CVE-2018-25107
Type: osv

## Details
The Crypt::Random::Source package before 0.13 for Perl has a fallback to the built-in rand() function, which is not a secure source of random bits.

## References
- https://metacpan.org/release/ETHER/Crypt-Random-Source-0.13/changes
- https://github.com/karenetheridge/Crypt-Random-Source/pull/3
