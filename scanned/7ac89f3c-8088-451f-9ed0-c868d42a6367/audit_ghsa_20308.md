# [M] Stack overflow in rustc_serialize when parsing deeply nested JSON

## Summary
Severity: Medium
Advisory: GHSA-2226-4v3c-cff8
Ecosystem: crates.io
Published: 2022-06-17
Source: https://github.com/advisories/GHSA-2226-4v3c-cff8
Type: github-advisory

## Affected
- crates.io: `rustc-serialize` — affected >=0

## Details
When parsing JSON using `json::Json::from_str`, there is no limit to the depth of the stack, therefore deeply nested objects can cause a stack overflow, which aborts the process.

Example code that triggers the vulnerability is

```rust
fn main() {
    let _ = rustc_serialize::json::Json::from_str(&"[0,[".repeat(10000));
}
```

[serde](https://crates.io/crates/serde) is recommended as a replacement to rustc_serialize.

## References
- https://github.com/rust-lang-deprecated/rustc-serialize
- https://github.com/rust-lang/rustc-serialize
- https://rustsec.org/advisories/RUSTSEC-2022-0004.html
