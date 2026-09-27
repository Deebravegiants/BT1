# [C] Cap'n Proto has Undefined Behavior in constant::Reader and StructSchema

## Summary
Severity: Critical
Advisory: GHSA-5w5r-mf82-595p
CWE: CWE-758
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-01-28
Source: https://github.com/advisories/GHSA-5w5r-mf82-595p
Type: github-advisory

## Affected
- crates.io: `capnp` — affected >=0 <0.24.0

## Details
The safe API functions `constant::Reader::get` and `StructSchema::new` rely on `PointerReader::get_root_unchecked`, which can cause undefined behavior (UB) by constructing arbitrary words or schemas.

## `Reader::get`

```rust
pub fn get(&self) -> Result<<T as Owned>::Reader<'static>> {
    // ...
    // UNSAFE: access `words` without validation
}
```

## `StructSchema::new`

```rust
pub fn new(builder: RawBrandedStructSchema) -> StructSchema {
    // ...
    // UNSAFE: access encoded nodes without validation
}
```

This vulnerability allows safe Rust code to trigger UB, which violates Rust's safety guarantees.

The issue is resolved in version `0.24.0` by making constructor functions unsafe and mark the fields of struct as visible only in the crate.

## References
- https://github.com/capnproto/capnproto-rust/issues/605
- https://github.com/capnproto/capnproto-rust/commit/7b981f4c75a975c80444cd38729bcdf12bf3eabf
- https://github.com/capnproto/capnproto-rust/commit/e3aeec213e6d1b30a182bf61682a370f20d8a02c
- https://github.com/capnproto/capnproto-rust
- https://rustsec.org/advisories/RUSTSEC-2025-0143.html
