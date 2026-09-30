# [?] fix(eth): break the transactionOfEncodedSize deadlock (#11259)

## Summary
Severity: Unknown
Chain: Ethereum
Component: hyperledger/besu
Published: 2026-09-09
Source: https://github.com/besu-eth/besu/commit/99918668353791ec55f56d05dbcda0b6bf358b82
Type: security-commit

## Details
fix(eth): break the transactionOfEncodedSize deadlock (#11259)

transactionOfEncodedSize searches for a payload length whose encoded
transaction lands exactly on a target size, re-sizing and re-signing up to
five times. Because a signature's r/s components are minimally RLP-encoded,
about one key pair in 256 signs one of the two candidate lengths a byte
short, and the search then cycles between them forever:

    L=130985 -> 131072   (short signature, one under target)
    L=130986 -> 131074   (full signature, one over target)
    L=130985 -> 131072   ...

No length reaches the target, so every attempt is spent and the helper
throws. KEY_PAIR1 is generated per JVM, so a bad key fails all four tests
that use the helper in that fork at once.

Vary a payload byte on each attempt as well as the length, so the same
length draws a fresh signature instead of the same one forever. Measured
over 3000 generated key pairs: 35 failures before, 0 after.

Signed-off-by: daniellehrner <daniel@lehrner.me>

## Patch
### ethereum/eth/src/test/java/org/hyperledger/besu/ethereum/eth/transactions/AbstractTransactionPoolTest.java
```diff
@@ -459,12 +459,15 @@ private Transaction transactionOfEncodedSize(final int targetEncodedSize) {
     // message. Since every payload length signs a different message, the overhead measured
     // against one transaction isn't guaranteed to carry over exactly to another: adjust and
     // re-sign until the actual encoded size lands on the target instead of assuming it will.
+    // Resizing alone can never get there for some keys, because the length one byte below the
+    // target and the one above both sign to a fixed size that straddles it, so each attempt
+    // also alters a payload byte to draw a different signature for the same length.
     int payloadSize = targetEncodedSize - encodedOverheadForLargePayload();
-    for (int attempt = 0; attempt < 5; attempt++) {
+    for (int attempt = 0; attempt < 16; attempt++) {
+      final byte[] payload = new byte[payloadSize];
+      payload[0] = (byte) attempt;
       final Transaction tx =
-          createBaseTransaction(0)
-              .payload(Bytes.wrap(new byte[payloadSize]))
-              .createTransaction(KEY_PAIR1);
+          createBaseTransaction(0).payload(Bytes.wrap(payload)).createTransaction(KEY_PAIR1);
       final int actualEncodedSize = tx.getSizeForBlockInclusion();
       if (actualEncodedSize == targetEncodedSize) {
         return tx;
```
