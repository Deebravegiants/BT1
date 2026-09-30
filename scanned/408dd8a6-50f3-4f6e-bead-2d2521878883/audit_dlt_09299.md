# [?] fix(common): avoid panic on invalid calldata selector by propagating parse error (#11888)

## Summary
Severity: Unknown
Chain: Tooling
Component: foundry-rs/foundry
Published: 2025-09-30
Source: https://github.com/foundry-rs/foundry/commit/90c7f9656f9ed17d3d48d5a94087f9fb52748653
Type: security-commit

## Details
fix(common): avoid panic on invalid calldata selector by propagating parse error (#11888)

## Patch
### crates/common/src/selectors.rs
```diff
@@ -217,7 +217,7 @@ impl OpenChainClient {
             )
         }
 
-        let mut sigs = self.decode_function_selector(calldata[..8].parse().unwrap()).await?;
+        let mut sigs = self.decode_function_selector(calldata[..8].parse()?).await?;
         // Retain only signatures that can be decoded.
         sigs.retain(|sig| abi_decode_calldata(sig, calldata, true, true).is_ok());
         Ok(sigs)
```
