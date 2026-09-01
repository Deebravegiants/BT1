# [?] fix: `RUSTSEC-2026-0007` (#10084)

## Summary
Severity: Unknown
Chain: IOTA
Component: iotaledger/iota
Published: 2026-02-05
Source: https://github.com/iotaledger/iota/commit/2b5a5d93f11384aaeee4dc90be8db603fbae8dd1
Type: security-commit

## Details
fix: `RUSTSEC-2026-0007` (#10084)

```
173 │ bytes 1.9.0 registry+https://github.com/rust-lang/crates.io-index
    │ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ security vulnerability detected
    │
    ├ ID: RUSTSEC-2026-0007
    ├ Advisory: https://rustsec.org/advisories/RUSTSEC-2026-0007
    ├ In the unique reclaim path of `BytesMut::reserve`, the condition
      ```rs
      if v_capacity >= new_cap + offset
      ```
      uses an unchecked addition. When `new_cap + offset` overflows `usize` in release builds, this condition may incorrectly pass, causing `self.cap` to be set to a value that exceeds the actual allocated capacity. Subsequent APIs such as `spare_capacity_mut()` then trust this corrupted `cap` value and may create out-of-bounds slices, leading to UB.
      
      This behavior is observable in release builds (integer overflow wraps), whereas debug builds panic due to overflow checks.
      
      ## PoC
      
      ```rs
      use bytes::*;
      
      fn main() {
          let mut a = BytesMut::from(&b"hello world"[..]);
          let mut b = a.split_off(5);
      
          // Ensure b becomes the unique owner of the backing storage
          drop(a);
      
          // Trigger overflow in new_cap + offset inside reserve
          b.reserve(usize::MAX - 6);
      
          // This call relies on the corrupted cap and may cause UB & HBO
          b.put_u8(b'h');
      }
      ```
      
      # Workarounds
      
```

_Trimmed to 38 lines — full report: https://github.com/iotaledger/iota/commit/2b5a5d93f11384aaeee4dc90be8db603fbae8dd1_
