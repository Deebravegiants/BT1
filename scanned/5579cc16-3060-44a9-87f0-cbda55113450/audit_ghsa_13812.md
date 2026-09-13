# [H] Insufficient covariance check makes self_cell unsound

## Summary
Severity: High
Advisory: GHSA-48m6-wm5p-rr6h
Ecosystem: crates.io
Published: 2023-11-14
Source: https://github.com/advisories/GHSA-48m6-wm5p-rr6h
Type: github-advisory

## Affected
- crates.io: `self_cell` — affected >=0 <0.10.3
- crates.io: `self_cell` — affected >=1.0.0 <1.0.2

## Details
All public versions prior to `1.02` used an insufficient check to ensure that users correctly marked the dependent type as either `covariant` or `not_covariant`. This allowed users to mark a dependent as covariant even though its type was not covariant but invariant, for certain invariant types involving trait object lifetimes. One example for such a dependent type is `type Dependent<'a> = RefCell<Box<dyn fmt::Display + 'a>>`. Such a type allowed unsound usage in purely safe user code that leads to undefined behavior. The patched versions now produce a compile time error if such a type is marked as `covariant`.

## References
- https://github.com/Voultapher/self_cell/issues/49
- https://github.com/Voultapher/self_cell
- https://rustsec.org/advisories/RUSTSEC-2023-0070.html
