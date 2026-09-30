# [M] bumpalo has use-after-free due to a lifetime error in `Vec::into_iter()`

## Summary
Severity: Medium
Advisory: GHSA-f85w-wvc7-crwc
Ecosystem: crates.io
Published: 2023-01-20
Source: https://github.com/advisories/GHSA-f85w-wvc7-crwc
Type: github-advisory

## Affected
- crates.io: `bumpalo` — affected >=1.1.0 <3.11.1

## Details
In affected versions of this crate, the lifetime of the iterator produced by `Vec::into_iter()` is not constrained to the lifetime of the `Bump` that allocated the vector's memory. Using the iterator after the `Bump` is dropped causes use-after-free accesses.

The following example demonstrates memory corruption arising from a misuse of this unsoundness.

```rust
use bumpalo::{collections::Vec, Bump};

fn main() {
    let bump = Bump::new();
    let mut vec = Vec::new_in(&bump);
    vec.extend([0x01u8; 32]);
    let into_iter = vec.into_iter();
    drop(bump);

    for _ in 0..100 {
        let reuse_bump = Bump::new();
        let _reuse_alloc = reuse_bump.alloc([0x41u8; 10]);
    }

    for x in into_iter {
        print!("0x{:02x} ", x);
    }
    println!();
}
```

The issue was corrected in version 3.11.1 by adding a lifetime to the `IntoIter` type, and updating the signature of `Vec::into_iter()` to constrain this lifetime.

## References
- https://github.com/fitzgen/bumpalo
- https://github.com/fitzgen/bumpalo/blob/main/CHANGELOG.md#3111
- https://rustsec.org/advisories/RUSTSEC-2022-0078.html
