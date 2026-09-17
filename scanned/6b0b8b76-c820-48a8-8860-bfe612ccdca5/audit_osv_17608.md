# [H] CVE-2020-17478

## Summary
Severity: High
Advisory: CVE-2020-17478
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-08-10
Source: https://osv.dev/vulnerability/CVE-2020-17478
Type: osv

## Details
ECDSA/EC/Point.pm in Crypt::Perl before 0.33 does not properly consider timing attacks against the EC point multiplication algorithm.

## References
- https://github.com/FGasper/p5-Crypt-Perl/compare/0.32...0.33
