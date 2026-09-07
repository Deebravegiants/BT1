# [H] fast-able is vulnerable to DoS attack through insecure method

## Summary
Severity: High
Advisory: GHSA-95hm-pr6q-298w
CWE: CWE-125
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-09-15
Source: https://github.com/advisories/GHSA-95hm-pr6q-298w
Type: github-advisory

## Affected
- crates.io: `fast-able` — affected >=0 <1.13.7

## Details
The public accessible struct SyncVec has a public safe method get_unchecked. It accept a parameter index and used in the get_unchecked without sufficient checks as mentioned [here](https://doc.rust-lang.org/std/primitive.slice.html#method.get_unchecked).

## References
- https://doc.rust-lang.org/std/primitive.slice.html#method.get_unchecked
- https://gitee.com/guoyucode/fast-able
- https://rustsec.org/advisories/RUSTSEC-2025-0063.html
