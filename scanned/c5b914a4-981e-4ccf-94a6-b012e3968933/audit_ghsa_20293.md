# [H] enum_map macro can cause UB when `Enum` trait is incorrectly implemented

## Summary
Severity: High
Advisory: GHSA-rxhx-9fj6-6h2m
Ecosystem: crates.io
Published: 2022-06-16
Source: https://github.com/advisories/GHSA-rxhx-9fj6-6h2m
Type: github-advisory

## Affected
- crates.io: `enum-map` — affected >=2.0.0-2 <2.0.2

## Details
Affected versions of this crate did not properly check the length of an enum when using `enum_map!` macro, trusting user-provided length.

When the `LENGTH` in the `Enum` trait does not match the array length in the `EnumArray` trait, this can result in the initialization of the enum map with uninitialized types, which in turn can allow an attacker to execute arbitrary code.

This problem can only occur with a manual implementation of the Enum trait, it will never occur for enums that use `#[derive(Enum)]`.

Example code that triggers this vulnerability looks like this:

```rust
enum E {
    A,
    B,
    C,
}

impl Enum for E {
    const LENGTH: usize = 2;

    fn from_usize(value: usize) -> E {
        match value {
            0 => E::A,
            1 => E::B,
            2 => E::C,
            _ => unimplemented!(),
        }
    }

    fn into_usize(self) -> usize {
        self as usize
    }
}

impl<V> EnumArray<V> for E {
    type Array = [V; 3];
}

let _map: EnumMap<E, String> = enum_map! { _ => "Hello, world!".into() };
```

The flaw was corrected in commit [b824e23](https://github.com/xfix/enum-map/commit/b824e232f2fb47837740070096ac253df8e80dfc) by putting `LENGTH` property on sealed trait for macro to read.

## References
- https://github.com/xfix/enum-map/commit/b824e232f2fb47837740070096ac253df8e80dfc
- https://github.com/rustsec/advisory-db/blob/main/crates/enum-map/RUSTSEC-2022-0010.md
- https://github.com/xfix/enum-map
- https://github.com/xfix/enum-map/blob/master/CHANGELOG.md#version-202
- https://gitlab.com/KonradBorowski/enum-map/-/blob/master/CHANGELOG.md#version-202
- https://rustsec.org/advisories/RUSTSEC-2022-0010.html
