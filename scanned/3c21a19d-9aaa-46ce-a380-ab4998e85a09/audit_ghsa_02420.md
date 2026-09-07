# [H] Unaligned references in sized-chunks

## Summary
Severity: High
Advisory: GHSA-fqpx-cq8x-9wp4
CVE: CVE-2020-25796
CWE: CWE-129
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-fqpx-cq8x-9wp4
Type: github-advisory

## Affected
- crates.io: `sized-chunks` — affected >=0 <0.6.3

## Details
An issue was discovered in the sized-chunks crate through 0.6.2 for Rust. In the InlineArray implementation, an unaligned reference may be generated for a type that has a large alignment requirement.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-25796
- https://github.com/bodil/sized-chunks/issues/11
- https://github.com/bodil/sized-chunks
- https://rustsec.org/advisories/RUSTSEC-2020-0041.html
