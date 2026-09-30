# [?] Add memory DoS prevention comments

## Summary
Severity: Unknown
Chain: Zcash
Component: ZcashFoundation/zebra
Published: 2021-03-21
Source: https://github.com/ZcashFoundation/zebra/commit/b623acc945668e3ad1ba7e5e228653ff8d333f80
Type: security-commit

## Details
Add memory DoS prevention comments

## Patch
### zebra-chain/src/transparent/serialize.rs
```diff
@@ -196,6 +196,7 @@ impl ZcashDeserialize for Input {
             if len > 100 {
                 return Err(SerializationError::Parse("coinbase has too much data"));
             }
+            // Memory Denial of Service: this length has just been checked
             let mut data = vec![0; len as usize];
             reader.read_exact(&mut data[..])?;
             let (height, data) = parse_coinbase_height(data)?;
```

### zebra-network/src/protocol/external/codec.rs
```diff
@@ -615,6 +615,7 @@ impl Codec {
 
         let filter_length: usize = min(body_len, MAX_FILTERADD_LENGTH);
 
+        // Memory Denial of Service: this length has just been bounded
         let mut filter_bytes = vec![0; filter_length];
         reader.read_exact(&mut filter_bytes)?;
 
```
