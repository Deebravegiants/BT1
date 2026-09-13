# [H] Path Traversal in rust-embed

## Summary
Severity: High
Advisory: GHSA-xrg3-hmf3-rvgw
CVE: CVE-2021-45712
CWE: CWE-22
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-01-06
Source: https://github.com/advisories/GHSA-xrg3-hmf3-rvgw
Type: github-advisory

## Affected
- crates.io: `rust-embed` — affected >=0 <6.3.0

## Details
When running in debug mode and the debug-embed (off by default) feature is not enabled, the generated get method does not check that the input path is a child of the folder given.

This allows attackers to read arbitrary files in the file system if they have control over the filename given. The following code will print the contents of your /etc/passwd if adjusted with a correct number of ../s depending on where it is run from.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-45712
- https://github.com/pyros2097/rust-embed/issues/159
- https://github.com/pyros2097/rust-embed
- https://raw.githubusercontent.com/rustsec/advisory-db/main/crates/rust-embed/RUSTSEC-2021-0126.md
- https://rustsec.org/advisories/RUSTSEC-2021-0126.html
