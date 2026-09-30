# [H] BIT-sass-2022-43357

## Summary
Severity: High
Advisory: BIT-sass-2022-43357
Aliases: CVE-2022-43357
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-sass-2022-43357
Type: osv

## Affected
- Bitnami: `sass` — affected >=3.6.5-8-g210218 <3.6.5

## Details
Stack overflow vulnerability in ast_selectors.cpp in function Sass::CompoundSelector::has_real_parent_ref in libsass:3.6.5-8-g210218, which can be exploited by attackers to causea denial of service (DoS). Also affects the command line driver for libsass, sassc 3.6.2.

## References
- https://drive.google.com/file/d/1aC5q3czen0atI91fuBIoCBFkS30_OSWX/
- https://github.com/sass/libsass
- https://github.com/sass/libsass/issues/3177
- https://nvd.nist.gov/vuln/detail/CVE-2022-43357
