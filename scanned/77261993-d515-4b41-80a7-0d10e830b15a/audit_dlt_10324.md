# [?] fix possible panic from short data length (#3751)

## Summary
Severity: Unknown
Chain: Solana
Component: solana-labs/solana-program-library
Published: 2022-10-26
Source: https://github.com/solana-labs/solana-program-library/commit/bf10dfddf4358f36759bb722cc028c2931fa09f6
Type: security-commit

## Details
fix possible panic from short data length (#3751)

## Patch
### token/program-2022/src/extension/mod.rs
```diff
@@ -244,6 +244,9 @@ fn get_extension<S: BaseState, V: Extension>(tlv_data: &[u8]) -> Result<&V, Prog
     // get_extension_indices has checked that tlv_data is long enough to include these indices
     let length = pod_from_bytes::<Length>(&tlv_data[length_start..value_start])?;
     let value_end = value_start.saturating_add(usize::from(*length));
+    if tlv_data.len() < value_end {
+        return Err(ProgramError::InvalidAccountData);
+    }
     pod_from_bytes::<V>(&tlv_data[value_start..value_end])
 }
 
@@ -933,6 +936,14 @@ mod test {
             state.get_extension::<TransferFeeConfig>(),
             Err(ProgramError::InvalidAccountData)
         );
+
+        // data buffer is too small
+        let buffer = &MINT_WITH_EXTENSION[..MINT_WITH_EXTENSION.len() - 1];
+        let state = StateWithExtensions::<Mint>::unpack(buffer).unwrap();
+        assert_eq!(
+            state.get_extension::<MintCloseAuthority>(),
+            Err(ProgramError::InvalidAccountData)
+        );
     }
 
     #[test]
```
