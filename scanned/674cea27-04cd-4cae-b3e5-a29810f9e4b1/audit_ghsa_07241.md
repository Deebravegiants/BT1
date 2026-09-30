# [M] OneRingBuf has a Use After Free Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-q95x-7g78-rccv
CWE: CWE-416
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:L/VI:L/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-08
Source: https://github.com/advisories/GHSA-q95x-7g78-rccv
Type: github-advisory

## Affected
- crates.io: `oneringbuf` — affected >=0 <0.8.0

## Details
Affected versions of `oneringbuf` exposed the obsolete `IntoRef::into_ref` method through the public `IntoRef` trait. For heap-backed ring buffers, this method returned a `DroppableRef` handle.

`DroppableRef` stored an owning raw pointer created from `Box::into_raw`. Its `Clone` implementation copied this raw pointer without incrementing the internal `alive_iters` counter. Internally, this clone pattern appears to rely on a fixed number of handles being created to match the initial `alive_iters` value. However, exposing `DroppableRef` through the public `IntoRef::TargetRef` associated type allows safe external code to create additional clones beyond that fixed count, breaking the lifetime protocol. `Drop` later dereferenced the pointer and could free the backing allocation with `Box::from_raw`.

Safe code could call `IntoRef::into_ref` to obtain a `DroppableRef` and then clone it. Each clone pointed to the same allocation, but the internal `alive_iters` counter was not increased. As a result, one clone could free the allocation while another clone still existed. Dropping the remaining clone then accessed freed memory, causing a heap-use-after-free.

The issue was fixed in version 0.8.0 by removing the obsolete `into_ref` method.

## Trigger

```rust
use oneringbuf::{IntoRef, LocalHeapRB};

fn main() {
    let rb = LocalHeapRB::<usize>::from(vec![1, 2, 3]);

    let r = <LocalHeapRB<usize> as IntoRef>::into_ref(rb);
    let r2 = r.clone();
    let r3 = r.clone();

    drop(r);
    drop(r2);
    drop(r3); // AddressSanitizer: heap-use-after-free
}
```

## References
- https://github.com/skilvingr/rust-oneringbuf/commit/643a24b30914068416dff9021a069c12c865a316
- https://github.com/Skilvingr/rust-oneringbuf
- https://rustsec.org/advisories/RUSTSEC-2026-0152.html
