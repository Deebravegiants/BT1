# [H] Array size is not checked in sized-chunks

## Summary
Severity: High
Advisory: GHSA-64gv-qg2v-vxv6
CVE: CVE-2020-25793
CWE: CWE-129
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-64gv-qg2v-vxv6
Type: github-advisory

## Affected
- crates.io: `sized-chunks` — affected >=0 <0.6.3

## Details
An issue was discovered in the sized-chunks crate through 0.6.2 for Rust. In the Chunk implementation, the array size is not checked when constructed with From<InlineArray<A, T>>.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-25793
- https://github.com/bodil/sized-chunks/issues/11
- https://github.com/bodil/sized-chunks
- https://rustsec.org/advisories/RUSTSEC-2020-0041.html
