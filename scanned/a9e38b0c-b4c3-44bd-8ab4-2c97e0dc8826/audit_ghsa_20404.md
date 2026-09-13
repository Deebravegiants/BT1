# [H] Out-of-bounds Write and Race Condition in metrics-util

## Summary
Severity: High
Advisory: GHSA-cwvc-87xq-pc5m
CVE: CVE-2021-45704
CWE: CWE-362, CWE-787
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-01-06
Source: https://github.com/advisories/GHSA-cwvc-87xq-pc5m
Type: github-advisory

## Affected
- crates.io: `metrics-util` — affected >=0 <0.7.0

## Details
In the affected versions of the crate, AtomicBucket<T> unconditionally implements Send/Sync traits. Therefore, users can create a data race to the inner T: !Sync by using the AtomicBucket::data_with() API. Such data races can potentially cause memory corruption or other undefined behavior.

The flaw was fixed in commit 8e6daab by adding appropriate Send/Sync bounds to the Send/Sync impl of struct Block<T> (which is a data type contained inside AtomicBucket<T>).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-45704
- https://github.com/metrics-rs/metrics/issues/190
- https://github.com/metrics-rs/metrics/commit/8e6daab
- https://github.com/metrics-rs/metrics
- https://raw.githubusercontent.com/rustsec/advisory-db/main/crates/metrics-util/RUSTSEC-2021-0113.md
- https://rustsec.org/advisories/RUSTSEC-2021-0113.html
