# [M] Data races in futures-intrusive

## Summary
Severity: Medium
Advisory: GHSA-4hjg-cx88-g9f9
CVE: CVE-2020-35915
CWE: CWE-362
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-4hjg-cx88-g9f9
Type: github-advisory

## Affected
- crates.io: `futures-intrusive` — affected >=0 <0.4.0

## Details
GenericMutexGuard<T> was given the Sync auto trait as long as T is Send due to its contained members. However, since the guard is supposed to represent an acquired lock and allows concurrent access to the underlying data from different threads, it should only be Sync when the underlying data is.

This is a soundness issue and allows data races, potentially leading to crashes and segfaults from safe Rust code.

The flaw was corrected by adding a T: Send + Sync bound for GenericMutexGuard's Sync trait.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-35915
- https://github.com/Matthias247/futures-intrusive/issues/53
- https://github.com/Matthias247/futures-intrusive
- https://rustsec.org/advisories/RUSTSEC-2020-0072.html
