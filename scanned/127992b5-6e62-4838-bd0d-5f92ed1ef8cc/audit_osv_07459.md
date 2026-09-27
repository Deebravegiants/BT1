# [H] BIT-sass-2022-43358

## Summary
Severity: High
Advisory: BIT-sass-2022-43358
Aliases: CVE-2022-43358
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-sass-2022-43358
Type: osv

## Affected
- Bitnami: `sass` — affected >=3.6.5-8-g210218 <3.6.5

## Details
Stack overflow vulnerability in ast_selectors.cpp: in function Sass::ComplexSelector::has_placeholder in libsass:3.6.5-8-g210218, which can be exploited by attackers to cause a denial of service (DoS).

## References
- https://drive.google.com/file/d/1j5fkPjWH9zQeTdO_4dMcZ-FpOBzP0MaI/
- https://github.com/sass/libsass
- https://github.com/sass/libsass/issues/3178
- https://nvd.nist.gov/vuln/detail/CVE-2022-43358
