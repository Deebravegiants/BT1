# [H] Stack overflow vulnerability in `ast_selectors.cpp` in function...

## Summary
Severity: High
Advisory: JLSEC-2026-664
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-13
Source: https://osv.dev/vulnerability/JLSEC-2026-664
Type: osv

## Affected
- Julia: `SassC_jll` — affected unspecified

## Details
Stack overflow vulnerability in `ast_selectors.cpp` in function `Sass::CompoundSelector::has_real_parent_ref` in libsass:3.6.5-8-g210218, which can be exploited by attackers to causea denial of service (DoS). Also affects the command line driver for libsass, sassc 3.6.2.

## References
- https://drive.google.com/file/d/1aC5q3czen0atI91fuBIoCBFkS30_OSWX
- https://drive.google.com/file/d/1aC5q3czen0atI91fuBIoCBFkS30_OSWX/
- https://github.com/advisories/GHSA-j7vr-2gc9-mmv7
- https://github.com/sass/libsass
- https://github.com/sass/libsass/issues/3177
- https://nvd.nist.gov/vuln/detail/CVE-2022-43357
