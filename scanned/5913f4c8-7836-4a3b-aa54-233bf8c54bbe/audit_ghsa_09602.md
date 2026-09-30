# [M] uutils coreutils has an Improper Input Validation Issue in its cut Utility

## Summary
Severity: Medium
Advisory: GHSA-m2pg-c7m6-77pj
CVE: CVE-2026-35380
CWE: CWE-20
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-04-22
Source: https://github.com/advisories/GHSA-m2pg-c7m6-77pj
Type: github-advisory

## Affected
- crates.io: `coreutils` — affected >=0 <0.8.0

## Details
A logic error in the cut utility of uutils coreutils causes the program to incorrectly interpret the literal two-byte string '' (two single quotes) as an empty delimiter. The implementation mistakenly maps this string to the NUL character for both the -d (delimiter) and --output-delimiter options. This vulnerability can lead to silent data corruption or logic errors in automated scripts and data pipelines that process strings containing these characters, as the utility may unintentionally split or join data on NUL bytes rather than the intended literal characters.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-35380
- https://github.com/uutils/coreutils/pull/11399
- https://github.com/uutils/coreutils/commit/593f5b191e8b9c87e4292955999c2d0b5cbcce69
- https://github.com/uutils/coreutils
- https://github.com/uutils/coreutils/releases/tag/0.8.0
