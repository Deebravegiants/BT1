# [M] pared Vulnerable to Use After Free in `Parc` and `Prc` Due to Missing Lifetime Constraints

## Summary
Severity: Medium
Advisory: GHSA-vgmh-mqm4-8j88
CWE: CWE-416
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2025-03-24
Source: https://github.com/advisories/GHSA-vgmh-mqm4-8j88
Type: github-advisory

## Affected
- crates.io: `pared` — affected >=0 <0.4.0

## Details
Affected versions of this crate didn't provide sufficient lifetime constraints to conversion functions from `alloc::sync::Arc` and `alloc::rc::Rc`, which made it possible to create projections of these reference counted pointers. Unlike the original reference counted pointers, these projections could outlive original data's lifetimes.

This projected pointer could cause the original `Arc`'s or `Rc`'s `Drop::drop` to get called at a point where the original data was no longer valid, leading to a potential use after free.

The affected functions were
- `pared::prc::Prc::from_rc`
- `pared::prc::Prc::project`
- `pared::prc::Prc::try_from_rc`
- `pared::sync::Parc::from_arc`
- `pared::sync::Parc::project`
- `pared::sync::Parc::try_from_arc`

This flaw was fixed in [108f540ea8acb6073751a1aa386085c1cdc4fd1e](https://github.com/radekvit/pared/commit/108f540ea8acb6073751a1aa386085c1cdc4fd1e) by requiring that the type stored in the `Arc`s and `Rc`s passed to these functions contain `T: 'static`.

## References
- https://github.com/radekvit/pared/issues/2
- https://github.com/radekvit/pared/commit/108f540ea8acb6073751a1aa386085c1cdc4fd1e
- https://github.com/radekvit/pared
- https://rustsec.org/advisories/RUSTSEC-2025-0016.html
