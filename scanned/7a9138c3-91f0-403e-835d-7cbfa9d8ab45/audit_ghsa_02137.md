# [H] Out of bounds write in stackvector

## Summary
Severity: High
Advisory: GHSA-9frf-r7c7-j2vg
CVE: CVE-2021-29939
CWE: CWE-787
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-9frf-r7c7-j2vg
Type: github-advisory

## Affected
- crates.io: `stackvector` — affected >=0 <1.0.9

## Details
StackVec::extend used the lower and upper bounds from an Iterator's size_hint to determine how many items to push into the stack based vector. If the size_hint implementation returned a lower bound that was larger than the upper bound, StackVec would write out of bounds and overwrite memory on the stack. As mentioned by the size_hint documentation, size_hint is mainly for optimization and incorrect implementations should not lead to memory safety issues.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-29939
- https://github.com/Alexhuszagh/rust-stackvector/issues/2
- https://github.com/Alexhuszagh/rust-stackvector
- https://rustsec.org/advisories/RUSTSEC-2021-0048.html
