# [H] CVE-2020-13895

## Summary
Severity: High
Advisory: CVE-2020-13895
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-06-07
Source: https://osv.dev/vulnerability/CVE-2020-13895
Type: osv

## Details
Crypt::Perl::ECDSA in the Crypt::Perl (aka p5-Crypt-Perl) module before 0.32 for Perl fails to verify correct ECDSA signatures when r and s are small and when s = 1. This happens when using the curve secp256r1 (prime256v1). This could conceivably have a security-relevant impact if an attacker wishes to use public r and s values when guessing whether signature verification will fail.

## References
- https://github.com/FGasper/p5-Crypt-Perl/issues/14
- https://github.com/FGasper/p5-Crypt-Perl/commit/f960ce75502acf7404187231a706672f8369acb2
