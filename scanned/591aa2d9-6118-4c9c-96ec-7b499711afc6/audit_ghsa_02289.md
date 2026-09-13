# [M] Data race in va-ts

## Summary
Severity: Medium
Advisory: GHSA-3hj2-hh36-hv9v
CVE: CVE-2020-36220
CWE: CWE-662, CWE-667, CWE-787
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-3hj2-hh36-hv9v
Type: github-advisory

## Affected
- crates.io: `va-ts` — affected >=0 <0.0.4

## Details
In the affected versions of this crate, Demuxer<T> unconditionally implemented Send with no trait bounds on T. This allows sending a non-Send type T across thread boundaries, which can cause undefined behavior like unlocking a mutex from a thread that didn't lock the mutex, or memory corruption from data race. The flaw was corrected in commit `0562cbf` by adding a T: Send bound to the Send impl for Demuxer<T>.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36220
- https://github.com/video-audio/va-ts/issues/4
- https://github.com/video-audio/va-ts
- https://rustsec.org/advisories/RUSTSEC-2020-0114.html
