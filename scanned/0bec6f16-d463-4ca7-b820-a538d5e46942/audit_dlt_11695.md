# [?] Merge bitcoin-core/secp256k1#952: Avoid computing out-of-bounds pointer.

## Summary
Severity: Unknown
Chain: Bitcoin
Component: bitcoin-core/secp256k1
Published: 2021-10-17
Source: https://github.com/bitcoin-core/secp256k1/commit/920a0e5fa642e1602ff092980d9a4abeb7bbfec6
Type: security-commit

## Details
Merge bitcoin-core/secp256k1#952: Avoid computing out-of-bounds pointer.

9be7b0f08340a063d961547b5d2663405f3fc162 Avoid computing out-of-bounds pointer. (Tim Ruffing)

Pull request description:

  This is a pedantic case of UB.

  Spotted in #879.

ACKs for top commit:
  elichai:
    ACK 9be7b0f08340a063d961547b5d2663405f3fc162
  practicalswift:
    cr ACK 9be7b0f08340a063d961547b5d2663405f3fc162
  sipa:
    ACK 9be7b0f08340a063d961547b5d2663405f3fc162

Tree-SHA512: a9d028c4cdb37ad0d5fcf0d2f678eef732a653d37155a69a20272c6b283c28e083172485d7a37dc4a7c6100b22a6f5b6a92e729239031be228cc511842ee35e8

## Patch
### src/ecdsa_impl.h
```diff
@@ -112,7 +112,7 @@ static int secp256k1_der_parse_integer(secp256k1_scalar *r, const unsigned char
     if (secp256k1_der_read_len(&rlen, sig, sigend) == 0) {
         return 0;
     }
-    if (rlen == 0 || *sig + rlen > sigend) {
+    if (rlen == 0 || rlen > (size_t)(sigend - *sig)) {
         /* Exceeds bounds or not at least length 1 (X.690-0207 8.3.1).  */
         return 0;
     }
```
