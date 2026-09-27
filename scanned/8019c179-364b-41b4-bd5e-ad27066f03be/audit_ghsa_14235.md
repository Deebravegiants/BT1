# [M] ntru-rs has unsound FFI: Wrong API usage causes write past allocated area

## Summary
Severity: Medium
Advisory: GHSA-fq33-vmhv-48xh
Ecosystem: crates.io
Published: 2023-04-07
Source: https://github.com/advisories/GHSA-fq33-vmhv-48xh
Type: github-advisory

## Affected
- crates.io: `ntru` — affected >=0.4.3

## Details
The following usage causes undefined behavior.
```rust
let kp: ntru::types::KeyPair = …;
kp.get_public().export(Default::default())
```

When compiled with debug assertions, the code above will trigger a `attempt to subtract with overflow` panic before UB occurs.
Other mistakes (e.g. using `EncParams` from a different key) may always trigger UB.

Likely, older versions of this crate are also affected, but have not been tested.

## References
- https://github.com/FrinkGlobal/ntru-rs/issues/8
- https://github.com/FrinkGlobal/ntru-rs
- https://rustsec.org/advisories/RUSTSEC-2023-0032.html
