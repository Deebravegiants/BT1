# [H] Data races in ticketed_lock

## Summary
Severity: High
Advisory: GHSA-77m6-x95j-75r5
CVE: CVE-2020-36439
CWE: CWE-119, CWE-362
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-77m6-x95j-75r5
Type: github-advisory

## Affected
- crates.io: `ticketed_lock` — affected >=0 <0.3.0

## Details
Affected versions of this crate unconditionally implemented Send for ReadTicket<T> & WriteTicket<T>. This allows to send non-Send T to other threads. This can allows creating data races by cloning types with internal mutability and sending them to other threads (as T of ReadTicket<T>/WriteTicket<T>). Such data races can cause memory corruption or other undefined behavior. The flaw was corrected in commit `a986a93` by adding T: Send bounds to Send impls of ReadTicket<T>/WriteTicket<T>.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36439
- https://github.com/kvark/ticketed_lock/issues/7
- https://github.com/kvark/ticketed_lock/commit/a986a9335d591fa5c826157d1674d47aa525357f
- https://github.com/kvark/ticketed_lock
- https://raw.githubusercontent.com/rustsec/advisory-db/main/crates/ticketed_lock/RUSTSEC-2020-0119.md
- https://rustsec.org/advisories/RUSTSEC-2020-0119.html
