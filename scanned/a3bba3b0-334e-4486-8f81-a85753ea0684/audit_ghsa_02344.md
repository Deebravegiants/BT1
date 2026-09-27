# [H] Out of bounds read in uu_od

## Summary
Severity: High
Advisory: GHSA-w9vv-q986-vj7x
CVE: CVE-2021-29934
CWE: CWE-125
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-w9vv-q986-vj7x
Type: github-advisory

## Affected
- crates.io: `uu_od` — affected >=0 <0.0.4

## Details
An issue was discovered in PartialReader in the uu_od crate before 0.0.4 for Rust. Attackers can read the contents of uninitialized memory locations via a user-provided Read operation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-29934
- https://github.com/uutils/coreutils/issues/1729
- https://github.com/uutils/coreutils/pull/1730
- https://github.com/uutils/coreutils/pull/1738
- https://github.com/uutils/coreutils/pull/1739
- https://github.com/uutils/coreutils/commit/39d62c6c1f809022c903180471c10fde6ecd12d1
- https://github.com/uutils/coreutils/commit/5935876f38498b0c1f657d031171eb17028def6f
- https://github.com/uutils/coreutils/commit/7341a1a033aa5980ac59bc9d4df978b396de4fad
- https://github.com/uutils/coreutils
- https://rustsec.org/advisories/RUSTSEC-2021-0043.html
