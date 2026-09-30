# [?] Fix potential out-of-bounds in resizing code

## Summary
Severity: Unknown
Chain: Zilliqa
Component: Zilliqa/zq1
Published: 2018-11-09
Source: https://github.com/Zilliqa/zq1/commit/28103cda87a5d78ab7b95fe41b262a09d092e5b3
Type: security-commit

## Details
Fix potential out-of-bounds in resizing code

## Patch
### src/libCrypto/Schnorr.cpp
```diff
@@ -99,10 +99,8 @@ void BIGNUMSerialize::SetNumber(vector<unsigned char>& dst, unsigned int offset,
   // if (actual_bn_size > 0)
   {
     if (actual_bn_size <= static_cast<int>(size)) {
-      const unsigned int length_available = dst.size() - offset;
-
-      if (length_available < size) {
-        dst.resize(dst.size() + size - length_available);
+      if (offset + size > dst.size()) {
+        dst.resize(offset + size);
       }
 
       // Pad with zeroes as needed
```
