# [M] Data races in try-mutex

## Summary
Severity: Medium
Advisory: GHSA-64j8-7gp2-xjx5
CVE: CVE-2020-35924
CWE: CWE-787
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-64j8-7gp2-xjx5
Type: github-advisory

## Affected
- crates.io: `try-mutex` — affected >=0 <0.3.0

## Details
Affected versions of this crate unconditionally implemented Sync trait for TryMutex<T> type. This allows users to put non-Send T type in TryMutex and send it to another thread, which can cause a data race. The flaw was corrected in the 0.3.0 release by adding T: Send bound for the Sync trait implementation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-35924
- https://github.com/mpdn/try-mutex/issues/2
- https://github.com/mpdn/try-mutex
- https://rustsec.org/advisories/RUSTSEC-2020-0087.html
