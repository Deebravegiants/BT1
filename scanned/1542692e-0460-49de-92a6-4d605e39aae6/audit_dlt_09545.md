# [?] fix MptValue primitive decode panic issue

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2026-05-21
Source: https://github.com/Conflux-Chain/conflux-rust/commit/ae7f56b743d4307f3e68e7925220c6c63206caef
Type: security-commit

## Details
fix MptValue primitive decode panic issue

## Patch
### crates/primitives/src/storage.rs
```diff
@@ -141,7 +141,7 @@ impl Decodable for MptValue<H256> {
             0u8 => Ok(MptValue::None),
             1u8 => Ok(MptValue::TombStone),
             2u8 => Ok(MptValue::Some(rlp.val_at(1)?)),
-            n => panic!("Unexpected MptValue type in RLP: {}", n),
+            _ => Err(DecoderError::Custom("Unexpected MptValue type in RLP")),
         }
     }
 }
@@ -252,6 +252,15 @@ mod tests {
         assert_eq!(val, rlp::decode(&rlp::encode(&val)).unwrap());
     }
 
+    #[test]
+    fn test_mpt_value_rlp_invalid_tag() {
+        let invalid = rlp::encode_list::<u8, _>(&[3]);
+        assert_eq!(
+            rlp::decode::<MptValue<MerkleHash>>(&invalid),
+            Err(rlp::DecoderError::Custom("Unexpected MptValue type in RLP"))
+        );
+    }
+
     #[test]
     fn test_mpt_value_json() {
         let val = MptValue::<MerkleHash>::None;
```
