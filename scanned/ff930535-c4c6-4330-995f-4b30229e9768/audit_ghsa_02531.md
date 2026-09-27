# [H] Data race in abox

## Summary
Severity: High
Advisory: GHSA-r626-fc64-3q28
CVE: CVE-2020-36441
CWE: CWE-119, CWE-362
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-r626-fc64-3q28
Type: github-advisory

## Affected
- crates.io: `abox` — affected >=0 <0.4.1

## Details
Affected versions of this crate implements `Send`/`Sync` for `AtomicBox<T>` without requiring `T: Send`/`T: Sync`. This allows to create data races to `T: !Sync` and send `T: !Send` to another thread. Such behavior breaks the compile-time thread safety guarantees of Rust, and allows users to incur undefined behavior using safe Rust (e.g. memory corruption from data race). The flaw was corrected in commit `34c2b9e` by adding trait bound `T: Send` to `Send` impl for `AtomicBox<T>` and trait bound `T: Sync` to `Sync` impl for `AtomicBox<T>`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36441
- https://github.com/SonicFrog/abox/issues/1
- https://github.com/SonicFrog/abox/pull/2
- https://github.com/SonicFrog/abox/commit/34c2b9e
- https://github.com/SonicFrog/abox
- https://raw.githubusercontent.com/rustsec/advisory-db/main/crates/abox/RUSTSEC-2020-0121.md
- https://rustsec.org/advisories/RUSTSEC-2020-0121.html
