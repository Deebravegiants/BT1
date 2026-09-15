# [H] Stack overflow in lopdf via deeply nested PDF objects

## Summary
Severity: High
Advisory: RUSTSEC-2026-0187
Ecosystem: crates.io
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-21
Source: https://osv.dev/vulnerability/RUSTSEC-2026-0187
Type: osv

## Affected
- crates.io: `lopdf` — affected >=0.0.0-0 <0.42.0

## Details
`lopdf::Document::load_mem` (and the other `load*` entry points) parses nested PDF arrays and dictionaries with unbounded recursion. A small crafted PDF whose Catalog contains a deeply nested array (`/X [[[ … ]]]`, on the order of 10,000 levels) exhausts the call stack and aborts the process with `SIGABRT`.

Because this is a stack-overflow abort rather than a `panic!`, it cannot be caught with `catch_unwind`: any service that parses untrusted PDF input with lopdf can be crashed by a ~21 KB file, resulting in a denial of service.

Confirmed on lopdf 0.41.0 and earlier; fixed in 0.42.0. Default configuration, no features changed.

## Proof of concept

```rust
fn main() {
    let bytes = std::fs::read("poc.pdf").unwrap(); // ~10,380-deep nested array in the Catalog
    let _ = lopdf::Document::load_mem(&bytes);     // stack overflow -> SIGABRT
}
```

An equivalent PoC is a minimal PDF whose Catalog `/X` value is `"[" * 10380 + "]" * 10380`.

## Suggested fix

Enforce a maximum object-nesting depth in the parser and return an `Err` instead of recursing without bound.

## References
- https://crates.io/crates/lopdf
- https://rustsec.org/advisories/RUSTSEC-2026-0187.html
- https://github.com/J-F-Liu/lopdf/issues/502
- https://github.com/J-F-Liu/lopdf/pull/503
- https://github.com/J-F-Liu/lopdf/commit/c755394
