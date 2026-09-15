# [M] Zerocopy: Some Ref methods are unsound with some type parameters

## Summary
Severity: Medium
Advisory: GHSA-rjhf-4mh8-9xjq
Ecosystem: crates.io
Published: 2023-12-18
Source: https://github.com/advisories/GHSA-rjhf-4mh8-9xjq
Type: github-advisory

## Affected
- crates.io: `zerocopy` — affected >=0.2.2 <0.2.9
- crates.io: `zerocopy` — affected >=0.3.0 <0.3.2
- crates.io: `zerocopy` — affected >=0.4.0 <0.4.1
- crates.io: `zerocopy` — affected >=0.5.0 <0.5.2
- crates.io: `zerocopy` — affected >=0.6.0 <0.6.6
- crates.io: `zerocopy` — affected >=0.7.0 <0.7.31

## Details
The `Ref` methods `into_ref`, `into_mut`, `into_slice`, and `into_slice_mut` are unsound and may allow safe code to exhibit undefined behavior when used with `Ref<B, T>` where `B` is [`cell::Ref`](https://doc.rust-lang.org/core/cell/struct.Ref.html) or [`cell::RefMut`](https://doc.rust-lang.org/core/cell/struct.RefMut.html). Note that these methods remain sound when used with `B` types other than `cell::Ref` or `cell::RefMut`.

See https://github.com/google/zerocopy/issues/716 for a more in-depth analysis.

The current plan is to yank the affected versions soon. See https://github.com/google/zerocopy/issues/679 for more detail.

## References
- https://github.com/google/zerocopy/issues/679
- https://github.com/google/zerocopy/issues/71
- https://github.com/google/zerocopy/issues/716
- https://github.com/google/zerocopy
- https://rustsec.org/advisories/RUSTSEC-2023-0074.html
