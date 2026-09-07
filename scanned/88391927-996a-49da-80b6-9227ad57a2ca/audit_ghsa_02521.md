# [H] Data race in syncpool

## Summary
Severity: High
Advisory: GHSA-vp6r-mrq9-8f4h
CVE: CVE-2020-36462
CWE: CWE-362, CWE-77
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-vp6r-mrq9-8f4h
Type: github-advisory

## Affected
- crates.io: `syncpool` — affected >=0 <0.1.6

## Details
Affected versions of this crate unconditionally implements Send for Bucket2. This allows sending non-Send types to other threads. This can lead to data races when non Send types like Cell<T> or Rc<T> are contained inside Bucket2 and sent across thread boundaries. The data races can potentially lead to memory corruption (as demonstrated in the PoC from the original report issue). The flaw was corrected in commit `15b2828` by adding a T: Send bound to the Send impl of Bucket2<T>.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36462
- https://github.com/Chopinsky/byte_buffer/issues/2
- https://github.com/Chopinsky/byte_buffer/commit/15b282877d1e576de2b337d8162bbf43ed1a0f2d
- https://github.com/Chopinsky/byte_buffer/tree/master/syncpool
- https://raw.githubusercontent.com/rustsec/advisory-db/main/crates/syncpool/RUSTSEC-2020-0142.md
- https://rustsec.org/advisories/RUSTSEC-2020-0142.html
