# [H] Data races in convec

## Summary
Severity: High
Advisory: GHSA-rpxm-vmr7-5f5f
CVE: CVE-2020-36445
CWE: CWE-119, CWE-362
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-rpxm-vmr7-5f5f
Type: github-advisory

## Affected
- crates.io: `convec` — affected >=0

## Details
Affected versions of this crate unconditionally implement Send/Sync for `ConVec<T>`.
This allows users to insert `T` that is not Send or not Sync.

This allows users to create data races by using non-Send types like `Arc<Cell<_>>` or `Rc<_>` as `T` in `ConVec<T>`. It is also possible to create data races by using types like `Cell<_>` or `RefCell<_>` as `T` (types that are `Send` but not `Sync`).
Such data races can lead to memory corruption.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36445
- https://github.com/krl/convec
- https://raw.githubusercontent.com/rustsec/advisory-db/main/crates/convec/RUSTSEC-2020-0125.md
- https://rustsec.org/advisories/RUSTSEC-2020-0125.html
