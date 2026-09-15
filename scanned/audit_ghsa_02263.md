# [H] Data races in cache

## Summary
Severity: High
Advisory: GHSA-g78p-g85h-q6ww
CVE: CVE-2020-36448
CWE: CWE-362, CWE-77
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-g78p-g85h-q6ww
Type: github-advisory

## Affected
- crates.io: `cache` — affected >=0

## Details
An issue was discovered in the cache crate through 2020-11-24 for Rust. 
Affected versions of this crate unconditionally implement Send/Sync for `Cache<K>`.
This allows users to insert `K` that is not Send or not Sync.

This allows users to create data races by using non-Send types like `Arc<Cell<T>>` or `Rc<T>` as `K` in `Cache<K>`. It is also possible to create data races by using types like `Cell<T>` or `RefCell<T>` (types that are `Send` but not `Sync`).
Such data races can lead to memory corruption.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36448
- https://github.com/krl/cache/issues/1
- https://github.com/krl/cache
- https://rustsec.org/advisories/RUSTSEC-2020-0128.html
