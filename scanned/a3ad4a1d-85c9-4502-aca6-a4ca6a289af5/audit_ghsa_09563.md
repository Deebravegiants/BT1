# [H] smallbitvec: Integer overflow in safe API leads to heap buffer overflow

## Summary
Severity: High
Advisory: GHSA-97wc-2hqc-cjgr
CVE: CVE-2026-44983
CWE: CWE-122, CWE-190
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H (CVSS_V3)
Published: 2026-05-09
Source: https://github.com/advisories/GHSA-97wc-2hqc-cjgr
Type: github-advisory

## Affected
- crates.io: `smallbitvec` — affected >=1.0.1

## Details
### Summary
An integer overflow in the internal capacity calculation of `smallbitvec` can lead to an undersized heap allocation, resulting in a heap buffer overflow through safe APIs only. This allows memory corruption without requiring `unsafe` code from the caller.

### Details
The issue originates from unchecked arithmetic in the internal helper function responsible for computing the required buffer size:

```
(cap + bits_per_storage() - 1) / bits_per_storage()
```

When `cap` is close to `usize::MAX`, the addition:

```
cap + bits_per_storage() - 1
```

can overflow in release builds and wrap around due to Rust’s default wrapping semantics for integer overflow in optimized builds.

As a result:
- `buffer_len(cap)` may return a value significantly smaller than required.
- The backing storage is allocated with insufficient size.
- Internal metadata (logical length/capacity) reflects a much larger size than the actual allocation.

Subsequent safe API calls (e.g., `set`, `push`, `reserve`) rely on this corrupted metadata and perform index computations that assume sufficient backing storage. These operations eventually reach unsafe internal code paths (e.g., pointer arithmetic and unchecked indexing), leading to out-of-bounds memory access.

Summary of the issue:
integer overflow
→ undersized allocation
→ inconsistent metadata (len/cap vs actual buffer)
→ unsafe internal access using corrupted metadata
→ heap buffer overflow (UB)
### PoC
#### PoC 1: Out-of-bounds write via `from_elem`
```rust
#![forbid(unsafe_code)]

use smallbitvec::SmallBitVec;

fn main() {
    // Triggers overflow in buffer_len(cap)
    let mut v = SmallBitVec::from_elem(usize::MAX, false);

    // Logical length is large, but backing storage is undersized
    // This leads to out-of-bounds write in unsafe internals
    v.set(0, true);
}
```
#### PoC 2: Overflow via `reserve`
```rust
#![forbid(unsafe_code)]

use smallbitvec::SmallBitVec;

fn main() {
    let mut v = SmallBitVec::new();
    v.push(true);

    // Triggers overflow in capacity computation
    v.reserve(usize::MAX - 10);
}
```

### Impact
- Heap buffer overflow via safe API only
- ASAN-observable heap-buffer-overflow
- Undefined Behavior detectable with Miri (e.g., out-of-bounds indexing due to corrupted metadata)

### Tested on
- rustc 1.96.0-nightly (9602bda1d 2026-04-05)
- Target: x86_64-unknown-linux-gnu
- Build: release
- ASAN: `RUSTFLAGS="-Z sanitizer=address" cargo +nightly run --release`
- Miri: `cargo +nightly miri run --release`

## References
- https://github.com/servo/smallbitvec/security/advisories/GHSA-97wc-2hqc-cjgr
- https://nvd.nist.gov/vuln/detail/CVE-2026-44983
- https://github.com/servo/smallbitvec
