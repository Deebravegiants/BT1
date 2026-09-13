# [H] Double free in slice-deque

## Summary
Severity: High
Advisory: GHSA-p9gf-gmfv-398m
CVE: CVE-2021-29938
CWE: CWE-415
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-p9gf-gmfv-398m
Type: github-advisory

## Affected
- crates.io: `slice-deque` — affected >=0

## Details
An issue was discovered in the slice-deque crate through 2021-02-19 for Rust. A double drop can occur in SliceDeque::drain_filter upon a panic in a predicate function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-29938
- https://github.com/gnzlbg/slice_deque/issues/90
- https://github.com/gnzlbg/slice_deque
- https://rustsec.org/advisories/RUSTSEC-2021-0047.html
