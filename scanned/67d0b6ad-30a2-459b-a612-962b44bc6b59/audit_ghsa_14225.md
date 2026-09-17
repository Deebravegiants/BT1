# [M] Adverserial use of `make_bitflags!` macro can cause undefined behavior

## Summary
Severity: Medium
Advisory: GHSA-qvc4-78gw-pv8p
Ecosystem: crates.io
Published: 2023-04-24
Source: https://github.com/advisories/GHSA-qvc4-78gw-pv8p
Type: github-advisory

## Affected
- crates.io: `enumflags2` — affected >=0.7.0 <0.7.7

## Details
The macro relied on an expression of the form `Enum::Variant` always being a
variant of the enum. However, it may also be an associated integer constant, in
which case there's no guarantee that the value of said constant consists only of
bits valid for this bitflag type.

Thus, code like this could create an invalid `BitFlags<Test>`, which would cause
iterating over it to trigger undefined behavior. As the debug formatter
internally iterates over the value, it is also affected.

```rust
use enumflags2::{bitflags, make_bitflags};

#[bitflags]
#[repr(u8)]
#[derive(Copy, Clone, Debug)]
enum Test {
    A = 1,
    B = 2,
}

impl Test {
    const C: u8 = 69;
}

fn main() {
    let x = make_bitflags!(Test::{C});
    // printing or iterating over x is UB
}
```

## References
- https://github.com/meithecatte/enumflags2
- https://github.com/meithecatte/enumflags2/releases/tag/v0.7.7
- https://rustsec.org/advisories/RUSTSEC-2023-0035.html
