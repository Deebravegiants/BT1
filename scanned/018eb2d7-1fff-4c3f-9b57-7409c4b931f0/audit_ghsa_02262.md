# [C] Memory corruption in smallvec

## Summary
Severity: Critical
Advisory: GHSA-69gw-hgj3-45m7
CVE: CVE-2019-15554
CWE: CWE-787
Ecosystem: crates.io
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-69gw-hgj3-45m7
Type: github-advisory

## Affected
- crates.io: `smallvec` — affected >=0.6.3 <0.6.10

## Details
Attempting to call grow on a spilled SmallVec with a value less than the current capacity causes corruption of memory allocator data structures. An attacker that controls the value passed to grow may exploit this flaw to obtain memory contents or gain remote code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-15554
- https://github.com/servo/rust-smallvec/issues/149
- https://github.com/servo/rust-smallvec
- https://rustsec.org/advisories/RUSTSEC-2019-0012.html
