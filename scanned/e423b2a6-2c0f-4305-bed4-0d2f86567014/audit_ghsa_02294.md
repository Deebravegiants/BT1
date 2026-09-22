# [C] Use of Uninitialized Resource in alg_ds

## Summary
Severity: Critical
Advisory: GHSA-3vv3-frrq-6486
CVE: CVE-2020-36432
CWE: CWE-665, CWE-908
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-3vv3-frrq-6486
Type: github-advisory

## Affected
- crates.io: `alg_ds` — affected >=0

## Details
An issue was discovered in the alg_ds crate through 2020-08-25 for Rust. `Matrix::new()` internally calls `Matrix::fill_with()` which uses `*ptr = value` pattern to initialize the buffer. This pattern assumes that there is an initialized struct at the address and drops it, which results in dropping of uninitialized struct.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36432
- https://gitlab.com/dvshapkin/alg-ds
- https://gitlab.com/dvshapkin/alg-ds/-/issues/1
- https://rustsec.org/advisories/RUSTSEC-2020-0033.html
