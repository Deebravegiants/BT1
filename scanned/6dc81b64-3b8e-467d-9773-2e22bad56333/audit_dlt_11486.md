# [?] fix(ci): remove no mangle from test panic handler (#1513)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cometbft/tendermint-rs
Published: 2025-11-21
Source: https://github.com/cometbft/tendermint-rs/commit/86f8d0778d1f50cce2beb42a34e2a671cb82c95c
Type: security-commit

## Details
fix(ci): remove no mangle from test panic handler (#1513)

## Patch
### tools/no-std-check/src/lib.rs
```diff
@@ -44,7 +44,6 @@ error[E0152]: found duplicate lang item `panic_impl`
  */
 #[cfg(feature = "panic-handler")]
 #[panic_handler]
-#[no_mangle]
 fn panic(_info: &PanicInfo) -> ! {
     loop {}
 }
```
