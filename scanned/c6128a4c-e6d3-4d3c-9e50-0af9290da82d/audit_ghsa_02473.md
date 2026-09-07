# [H] Data race in v9

## Summary
Severity: High
Advisory: GHSA-3837-87vh-xq3w
CVE: CVE-2020-36447
CWE: CWE-77
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-3837-87vh-xq3w
Type: github-advisory

## Affected
- crates.io: `v9` — affected >=0 <0.1.43

## Details
Affected versions of this crate unconditionally implement Sync for SyncRef<T>. This definition allows data races if &T is accessible through &SyncRef.

SyncRef<T> derives Clone and Debug, and the default implementations of those traits access &T by invoking T::clone() & T::fmt(). It is possible to create data races & undefined behavior by concurrently invoking SyncRef<T>::clone() or SyncRef<T>::fmt() from multiple threads with T: !Sync.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36447
- https://github.com/purpleposeidon/v9/issues/1
- https://github.com/purpleposeidon/v9/commit/18847c50e5d36561cc91c996c3539ddb1eacf6c7
- https://github.com/purpleposeidon/v9
- https://raw.githubusercontent.com/rustsec/advisory-db/main/crates/v9/RUSTSEC-2020-0127.md
- https://rustsec.org/advisories/RUSTSEC-2020-0127.html
