# [?] fix(p2p): avoid 32-bit overflow in attestation pool block position key (#22412)

## Summary
Severity: Unknown
Chain: Aztec
Component: AztecProtocol/aztec-packages
Published: 2026-04-09
Source: https://github.com/AztecProtocol/aztec-packages/commit/6b698eeacdd58525bb19d520dceba1c35549a908
Type: security-commit

## Details
fix(p2p): avoid 32-bit overflow in attestation pool block position key (#22412)

## Summary
- Replace bit-shift (`<<`) with multiplication in
`AttestationPool.getBlockPositionKey` to prevent 32-bit signed integer
overflow on large slot numbers. JavaScript's `<<` converts operands to
signed 32-bit ints, which overflows after slot ~2^21. Using
multiplication keeps values in float64 range (safe up to 2^53).

Fixes
[A-760](https://linear.app/aztec-labs/issue/A-760/audit-91-attestationpoolgetblockpositionkey-bit-shift-overflow-after)

## Patch
### yarn-project/p2p/src/mem_pools/attestation_pool/attestation_pool.ts
```diff
@@ -154,14 +154,16 @@ export class AttestationPool {
   /** Maximum indexWithinCheckpoint value (2^10 - 1 = 1023). */
   private static readonly MAX_INDEX = (1 << AttestationPool.INDEX_BITS) - 1;
 
-  /** Creates a position key for block proposals: (slot << 10) | indexWithinCheckpoint. */
+  /** Creates a position key for block proposals: slot * 1024 + indexWithinCheckpoint.
+   * Uses multiplication instead of bit-shift to avoid 32-bit signed integer overflow
+   * (bit-shift overflows after slot ~2^21, roughly 278 days of uptime). */
   private getBlockPositionKey(slot: number, indexWithinCheckpoint: number): number {
     if (indexWithinCheckpoint > AttestationPool.MAX_INDEX) {
       throw new Error(
         `Value for indexWithinCheckpoint ${indexWithinCheckpoint} exceeds maximum ${AttestationPool.MAX_INDEX}`,
       );
     }
-    return (slot << AttestationPool.INDEX_BITS) | indexWithinCheckpoint;
+    return slot * (1 << AttestationPool.INDEX_BITS) + indexWithinCheckpoint;
   }
 
   /**
@@ -454,7 +456,7 @@ export class AttestationPool {
 
       // Delete block proposals for slots < oldestSlot, using blockProposalsForSlotAndIndex as index
       // Key format: (slot << INDEX_BITS) | indexWithinCheckpoint
-      const blockPositionEndKey = oldestSlot << AttestationPool.INDEX_BITS;
+      const blockPositionEndKey = oldestSlot * (1 << AttestationPool.INDEX_BITS);
       for await (const positionKey of this.blockProposalsForSlotAndIndex.keysAsync({ end: blockPositionEndKey })) {
         const proposalIds = await toArray(this.blockProposalsForSlotAndIndex.getValuesAsync(positionKey));
         for (const proposalId of proposalIds) {
```
