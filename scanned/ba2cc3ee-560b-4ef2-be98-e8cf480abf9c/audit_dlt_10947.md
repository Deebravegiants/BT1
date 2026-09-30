# [?] Avoid panic during cast in verify (#3740)

## Summary
Severity: Unknown
Chain: ZK
Component: risc0/risc0
Published: 2026-04-06
Source: https://github.com/risc0/risc0/commit/c0ae7ba1a9ffbcc12f974bfc1ec25f7adaf96414
Type: security-commit

## Details
Avoid panic during cast in verify (#3740)

## Patch
### risc0/circuit/rv32im/src/lib.rs
```diff
@@ -131,18 +131,18 @@ impl<'a> Decoder<'a> {
     }
 
     fn read_u32_from_elem(&mut self) -> Result<u32> {
-        Ok(bytemuck::checked::cast::<_, Elem>(self.read_u32()?).as_u32())
+        Ok(try_cast(self.read_u32()?)?.as_u32())
     }
 
     fn read_u32_from_shorts(&mut self) -> Result<u32> {
-        let slice = bytemuck::checked::cast_slice::<_, Elem>(self.read(2)?);
+        let slice = try_cast_slice(self.read(2)?)?;
         let (high, low) = (slice[1], slice[0]);
         let val = (high.as_u32() & 0xffff) << 16 | (low.as_u32() & 0xffff);
         Ok(val)
     }
 
     fn read_digest_from_words(&mut self) -> Result<Digest> {
-        let slice = bytemuck::checked::cast_slice::<_, Elem>(self.read(DIGEST_WORDS)?);
+        let slice = try_cast_slice(self.read(DIGEST_WORDS)?)?;
         let buf = slice.iter().map(|x| x.as_u32()).collect::<Vec<u32>>();
         Ok(Digest::try_from(buf).unwrap())
     }
@@ -151,7 +151,7 @@ impl<'a> Decoder<'a> {
         let slice = self.read(DIGEST_SHORTS)?;
         let mut digest_bytes = [0; DIGEST_BYTES];
         for i in 0..DIGEST_SHORTS {
-            let elem: Elem = bytemuck::checked::cast(slice[i]);
+            let elem = try_cast(slice[i])?;
             let word = elem.as_u32();
             let short =
                 u16::try_from(word).map_err(|e| anyhow!("failed to convert u32 to u16: {e}"))?;
@@ -162,6 +162,14 @@ impl<'a> Decoder<'a> {
     }
 }
 
+fn try_cast(raw: u32) -> Result<Elem> {
+    bytemuck::checked::try_cast(raw).map_err(|e| anyhow!(e))
+}
+
+fn try_cast_slice(slice: &[u32]) -> Result<&[Elem]> {
+    bytemuck::checked::try_cast_slice(slice).map_err(|e| anyhow!(e))
+}
+
 impl Claim {
     pub fn decode(seal: &[u32]) -> Result<Self> {
         let mut decoder = Decoder::new(seal);
```

### risc0/zkvm/src/receipt/succinct.rs
```diff
@@ -169,7 +169,8 @@ impl<Claim> SuccinctReceipt<Claim> {
 
         // Extract the globals from the seal
         let output_elems: &[BabyBearElem] =
-            bytemuck::checked::cast_slice(&self.seal[..CircuitImpl::OUTPUT_SIZE]);
+            bytemuck::checked::try_cast_slice(&self.seal[..CircuitImpl::OUTPUT_SIZE])
+                .map_err(|_| VerificationError::ReceiptFormatError)?;
         let mut seal_claim = VecDeque::new();
         for elem in output_elems {
             seal_claim.push_back(elem.as_u32())
```
