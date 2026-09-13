# [C] Buffer overflow in SmallVec::insert_many

## Summary
Severity: Critical
Advisory: GHSA-43w2-9j62-hq99
CVE: CVE-2021-25900
CWE: CWE-787
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-43w2-9j62-hq99
Type: github-advisory

## Affected
- crates.io: `smallvec` — affected >=0.6.3 <0.6.14
- crates.io: `smallvec` — affected >=1.0.0 <1.6.1

## Details
A bug in the SmallVec::insert_many method caused it to allocate a buffer that was smaller than needed. It then wrote past the end of the buffer, causing a buffer overflow and memory corruption on the heap. This bug was only triggered if the iterator passed to insert_many yielded more items than the lower bound returned from its size_hint method.

The flaw was corrected in smallvec 0.6.14 and 1.6.1, by ensuring that additional space is always reserved for each item inserted. The fix also simplified the implementation of insert_many to use less unsafe code, so it is easier to verify its correctness.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-25900
- https://github.com/servo/rust-smallvec/issues/252
- https://github.com/servo/rust-smallvec/commit/5757ac500d4e544485d796b542e4e589749c291b
- https://github.com/servo/rust-smallvec/commit/9998ba0694a6b51aa6604748b00b6a98f0a0039e
- https://github.com/servo/rust-smallvec
- https://rustsec.org/advisories/RUSTSEC-2021-0003.html
