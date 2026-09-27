# [H] Improper Input Validation in once_cell

## Summary
Severity: High
Advisory: GHSA-7j44-fv4x-79g9
CVE: CVE-2019-16141
CWE: CWE-20
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-7j44-fv4x-79g9
Type: github-advisory

## Affected
- crates.io: `once_cell` — affected >=0.2.5 <1.0.1

## Details
If during the first dereference of Lazy the initialization function panics, subsequent dereferences will execute std::hints::unreachable_unchecked. Applications with panic = "abort" are not affected, as there will be no subsequent dereferences.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-16141
- https://github.com/matklad/once_cell/issues/46
- https://github.com/matklad/once_cell/pull/47
- https://github.com/matklad/once_cell/commit/afcca95a05240ebd931ab20998c946f77ef1e284
- https://github.com/matklad/once_cell
- https://rustsec.org/advisories/RUSTSEC-2019-0017.html
