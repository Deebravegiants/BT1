# [?] Remove double spend consensus parameter (#2669)

## Summary
Severity: Unknown
Chain: Iron Fish
Component: iron-fish/ironfish
Published: 2022-11-30
Source: https://github.com/iron-fish/ironfish/commit/073a2e3487a96f37fb1821be45fe971b59829429
Type: security-commit

## Details
Remove double spend consensus parameter (#2669)

## Patch
### ironfish/src/blockchain/blockchain.test.ts
```diff
@@ -739,17 +739,8 @@ describe('Blockchain', () => {
   })
 
   it('rejects double spend transactions', async () => {
-    /**
-     * This test tests that our double spend code is working properly. We had a
-     * bug that allowed double spends, but fixed the bug at roughly 200k blocks
-     * in. So we need to test that blocks are allowed in before the block
-     * activation of the fix.
-     */
     const { node, chain } = await nodeTest.createSetup()
 
-    // Set this up so we can reject block with a double spend starting at sequence 5
-    node.chain.consensus.V1_DOUBLE_SPEND = 5
-
     const accountA = await useAccountFixture(node.wallet, 'accountA')
     const accountB = await useAccountFixture(node.wallet, 'accountB')
 
@@ -759,74 +750,44 @@ describe('Blockchain', () => {
     // Now create the double spend
     await node.wallet.updateHead()
     const tx = await useTxFixture(node.wallet, accountA, accountB)
-    const doubleSpend = tx.getSpend(0)
-
-    const treeSize = await node.chain.nullifiers.size()
 
-    // The nullifier is not found in the tree
-    await expect(node.chain.nullifiers.contains(doubleSpend.nullifier)).resolves.toBe(false)
-    await expect(
-      node.chain.nullifiers.contained(doubleSpend.nullifier, treeSize),
-    ).resolves.toBe(false)
-
-    // Let's spend the transaaction for the first time
+    // Spend the transaaction for the first time
     const block3 = await useMinerBlockFixture(node.chain, 3, undefined, undefined, [tx])
     await expect(node.chain).toAddBlock(block3)
 
-    // The nullifier is not found at the old tree size, but is found at the new tree size
-    await expect(node.chain.nullifiers.contains(doubleSpend.nullifier)).resolves.toBe(true)
-    await expect(
-      node.chain.nullifiers.contained(doubleSpend.nullifier, treeSize),
-    ).resolves.toBe(false)
-    await expect(
-      node.chain.nullifiers.contained(doubleSpend.nullifier, treeSize + tx.spendsLength()),
-    ).resolves.toBe(true)
-
-    // Let's spend the transaction a second time
+    // Spend the transaction a second time
     const block4 = await useMinerBlockFixture(node.chain, 4, undefined, undefined, [tx])
-    await expect(node.chain).toAddBlock(block4)
-
-    // We've now added a double spend, we can see that because of a bug in the
-    // MerkleTree implementation the nullifier is no longer found at the tree
-    // size before this block, but moved to the tree size at block3
-    await expect(node.chain.nullifiers.contains(doubleSpend.nullifier)).resolves.toBe(true)
-    await expect(
-      node.chain.nullifiers.contained(doubleSpend.nullifier, treeSize + tx.spendsLength()),
-    ).resolves.toBe(false)
-    await expect(
-      node.chain.nullifiers.contained(
-        doubleSpend.nullifier,
-        treeSize + tx.spendsLength() + tx.spendsLength(),
-      ),
-    ).resolves.toBe(true)
-
-    // Now we set our fix to activate at sequence 5 so this block will not let
-    // us add the transaction a third time
-    const block5 = await useMinerBlockFixture(node.chain, 5, undefined, undefined, [tx])
-    await expect(node.chain.addBlock(block5)).resolves.toMatchObject({
+    await expect(node.chain.addBlock(block4)).resolves.toMatchObject({
       isAdded: false,
       reason: VerificationResultReason.DOUBLE_SPEND,
     })
   })
 
   it('rejects double spend during reorg', async () => {
-    // G -> A2 -> A3
-    //   -> B2 -> B3* -> A4
+    /**
+     * We don't check double spends when connecting forks because we don't rebuild the nullifier
+     * set unless we're adding to the head. If we re-org to a fork that contains a double spend
+     * though, we should catch that
+     *
+     * G -> A2 -> A3 -> A4 -> A5
+     *   -> B2 -> B3* -> B4* -> B5 -> B6
+     */
+
     const { node: nodeA } = await nodeTest.createSetup()
     const { node: nodeB } = await nodeTest.createSetup()
 
-    nodeA.chain.consensus.V1_DOUBLE_SPEND = 0
-    nodeB.chain.consensus.V1_DOUBLE_SPEND = 5
-
     const blockA2 = await useMinerBlockFixture(nodeA.chain, 2)
     await expect(nodeA.chain).toAddBlock(blockA2)
     const blockA3 = await useMinerBlockFixture(nodeA.chain, 3)
     await expect(nodeA.chain).toAddBlock(blockA3)
     const blockA4 = await useMinerBlockFixture(nodeA.chain, 4)
     await expect(nodeA.chain).toAddBlock(blockA4)
-    const blockA5 = await useMinerBlockFixture(nodeA.chain, 4)
+    const blockA5 = await useMinerBlockFixture(nodeA.chain, 5)
     await expect(nodeA.chain).toAddBlock(blockA5)
 
+    // create one more block to add at the end
+    const blockA6 = await useMinerBlockFixture(nodeA.chain, 6)
+
     const accountA = await useAccountFixture(nodeB.wallet, 'accountA')
     const accountB = await useAccountFixture(nodeB.wallet, 'accountB')
 
@@ -842,7 +803,8 @@ describe('Blockchain', () => {
     await expect(nodeB.chain).toAddBlock(blockB3)
 
     const blockB4 = await useMinerBlockFixture(nodeB.chain, 4, undefined, undefined, [tx])
-    await expect(nodeB.chain).toAddBlock(blockB4)
+
+    await expect(nodeB.chain).toAddDoubleSpendBlock(blockB4)
 
     const blockB5 = await useMinerBlockFixture(nodeB.chain, 5)
     await expect(nodeB.chain).toAddBlock(blockB5)
@@ -870,12 +832,14 @@ describe('Blockchain', () => {
     const addedB6 = await nodeA.chain.addBlock(blockB6)
 
     if (!addedB5.isAdded) {
+      expect(nodeA.chain.head.hash.equals(blockB3.header.hash)).toBe(true)
       expect(addedB5).toMatchObject({
         isAdded: false,
         isFork: null,
         reason: VerificationResultReason.DOUBLE_SPEND,
       })
     } else {
+      expect(nodeA.chain.head.hash.equals(blockB3.header.hash)).toBe(true)
       expect(addedB5).toMatchObject({
         isAdded: true,
         isFork: true,
@@ -887,107 +851,10 @@ describe('Blockchain', () => {
         reason: VerificationResultReason.DOUBLE_SPEND,
       })
     }
-  })
-
-  it('does not remove nullifiers from double spends during reorg', async () => {
-    // chain diagram for test duration, double spend transaction represented as '*'
-    //
-    // nodeA chain
-    // G -> B2 -> B3* -> A4*
-    //                -> B4  -> B5 -> B6*
-    //
-    // nodeB chain
-    // G -> B2 -> B3* -> B4  -> B5
-    const { node: nodeA } = await nodeTest.createSetup()
-    const { node: nodeB } = await nodeTest.createSetup()
-
-    // nodeA will reject double spends after block 5, nodeB will always reject them
-    nodeA.chain.consensus.V1_DOUBLE_SPEND = 5
-    nodeB.chain.consensus.V1_DOUBLE_SPEND = 0
-
-    const accountA = await useAccountFixture(nodeB.wallet, 'accountA')
-    const accountB = await useAccountFixture(nodeB.wallet, 'accountB')
-
-    // create the chain
-    // nodeA chain
-    // G -> B2
-    //
-    // nodeB chain
-    // G -> B2
-    const blockB2 = await useMinerBlockFixture(nodeB.chain, 2, accountA)
-    await expect(nodeB.chain).toAddBlock(blockB2)
-    await expect(nodeA.chain).toAddBlock(blockB2)
-
-    // create the double spend tx
-    // nodeA chain
-    // G -> B2 -> B3*
-    //
-    // nodeB chain
-    // G -> B2 -> B3*
-    await nodeB.wallet.updateHead()
-    const tx = await useTxFixture(nodeB.wallet, accountA, accountB)
-
-    const blockB3 = await useMinerBlockFixture(nodeB.chain, 3, undefined, undefined, [tx])
-    await expect(nodeB.chain).toAddBlock(blockB3)
-    await expect(nodeA.chain).toAddBlock(blockB3)
-
-    // create a fork with a double spend
-    // nodeA chain
-    // G -> B2 -> B3* -> A4*
-    const blockA4 = await useMinerBlockFixture(nodeA.chain, 4, undefined, undefined, [tx])
-    await expect(nodeA.chain).toAddBlock(blockA4)
-
-    // continue the main chain
-    // nodeA chain
-    // G -> B2 -> B3* -> A4*
-    //
-    // nodeB chain
-    // G -> B2 -> B3* -> B4  -> B5
-    const blockB4 = await useMinerBlockFixture(nodeB.chain, 4)
-    await expect(nodeB.chain).toAddBlock(blockB4)
-
-    const blockB5 = await useMinerBlockFixture(nodeB.chain, 5)
-    await expect(nodeB.chain).toAddBlock(blockB5)
-
-    // now start adding the main chain until we reorg to it
-    // nodeA chain
-    // G -> B2 -> B3* -> B4  -> B5
-    //                -> A4*
-    //
-    // nodeB chain
-    // G -> B2 -> B3* -> B4  -> B5
-    await expect(nodeA.chain).toAddBlock(blockB4)
-    await expect(nodeA.chain).toAddBlock(blockB5)
-
-    // chain B should contain the nullifiers from the double spend transaction
-    for (const spend of tx.spends()) {
-      await expect(nodeB.chain.nullifiers.contains(spend.nullifier)).resolves.toBe(true)
-    }
-
-    // chain A's nullifiers store is corrupt, and is missing the nullifiers
-    for (const spend of tx.spends()) {
-      await expect(nodeA.chain.nullifiers.contains(spend.nullifier)).resolves.toBe(false)
-    }
 
-    // create another block with a double spend
-    const blockA6 = await useMinerBlockFixture(nodeB.chain, 6, undefined, undefined, [tx])
-
-    // chain B should not add it
-    await expect(nodeB.chain.addBlock(blockA6)).resolves.toMatchObject({
-      isAdded: false,
-      isFork: null,
-      reason: VerificationResultReason.DOUBLE_SPEND,
-    })
-
-    // chain A should not add it, since it is past its V1_DOUBLE_SPEND conensus change sequence (5)
-    // but it does because its nullifiers store is corrupt
-    // nodeA chain
-    // G -> B2 -> B3* -> B4  -> B5 -> B6*
-    //                -> A4*
-    await expect(nodeA.chain.addBlock(blockA6)).resolves.toMatchObject({
-      isAdded: true,
-      isFork: false,
-    })
+    // The chain should re-org back to the valid chain once it sees the next block
+    await expect(nodeA.chain).toAddBlock(blockA6)
+    expect(nodeA.chain.head.hash.equals(blockA6.header.hash)).toBe(true)
   })
 
   it('does not grant mining reward after V3_DISABLE_MINING_REWARD', async () => {
```

### ironfish/src/consensus/consensus.ts
```diff
@@ -71,14 +71,6 @@ export class ConsensusParameters {
    */
   MAX_BLOCK_SIZE_BYTES = 2000000
 
-  /**
-   * Before upgrade V1 we had double spends. At this block we do a double spend
-   * check to disallow it.
-   *
-   * TODO: remove this sequence check before mainnet
-   */
-  V1_DOUBLE_SPEND = 0
-
   /**
    * Before upgrade V2 we didn't enforce max block size.
    * At this block we check that the block size doesn't exceed MAX_BLOCK_SIZE_BYTES.
@@ -100,7 +92,6 @@ export class ConsensusParameters {
 export class TestnetParameters extends ConsensusParameters {
   constructor() {
     super()
-    this.V1_DOUBLE_SPEND = 204000
     this.V2_MAX_BLOCK_SIZE = 255000
     this.V3_DISABLE_MINING_REWARD = 279900
   }
```

### ironfish/src/consensus/verifier.test.ts
```diff
@@ -216,24 +216,6 @@ describe('Verifier', () => {
       expect(Array.from(block.spends())).toHaveLength(1)
     })
 
-    it('is invalid with DOUBLE_SPEND as the reason', async () => {
-      const { chain } = nodeTest
-      const { block } = await useBlockWithTx(nodeTest.node)
-
-      const spends = Array.from(block.spends())
-      jest.spyOn(block, 'spends').mockImplementationOnce(function* () {
-        for (const spend of spends) {
-          yield spend
-          yield spend
-        }
-      })
-
-      expect(await chain.verifier.verifyConnectedSpends(block)).toEqual({
-        valid: false,
-        reason: VerificationResultReason.DOUBLE_SPEND,
-      })
-    })
-
     it('is invalid with ERROR as the reason', async () => {
       const { block } = await useBlockWithTx(nodeTest.node)
 
@@ -419,21 +401,5 @@ describe('Verifier', () => {
         },
       )
     })
-
-    it('returns any error from verifyConnectedSpends()', async () => {
-      const genesisBlock = await nodeTest.chain.getBlock(nodeTest.chain.genesis)
-      Assert.isNotNull(genesisBlock)
-
-      jest
-        .spyOn(nodeTest.verifier, 'verifySpend')
-        .mockResolvedValue(VerificationResultReason.ERROR)
-
-      await expect(nodeTest.verifier.verifyConnectedBlock(genesisBlock)).resolves.toMatchObject(
-        {
-          valid: false,
-          reason: VerificationResultReason.ERROR,
-        },
-      )
-    })
   })
 })
```

### ironfish/src/consensus/verifier.ts
```diff
@@ -264,14 +264,17 @@ export class Verifier {
   ): Promise<VerificationResult> {
     return this.chain.db.withTransaction(tx, async (tx) => {
       const notesSize = await this.chain.notes.size(tx)
-      const nullifierSize = await this.chain.nullifiers.size(tx)
 
       for (const spend of transaction.spends()) {
-        const reason = await this.verifySpend(spend, notesSize, nullifierSize, tx)
+        const reason = await this.verifySpend(spend, notesSize, tx)
 
         if (reason) {
           return { valid: false, reason }
         }
+
+        if (await this.chain.nullifiers.contains(spend.nullifier, tx)) {
+          return { valid: false, reason: VerificationResultReason.DOUBLE_SPEND }
+        }
       }
 
       return { valid: true }
@@ -352,86 +355,57 @@ export class Verifier {
     tx?: IDatabaseTransaction,
   ): Promise<VerificationResult> {
     return this.chain.db.withTransaction(tx, async (tx) => {
-      const { nullifiers: nullifiersCount } = block.counts()
-      const processedSpends = new BufferSet()
-
       const previousNotesSize = block.header.noteSize
       Assert.isNotNull(previousNotesSize)
-      const previousNullifierSize = block.header.nullifierCommitment.size - nullifiersCount
 
       for (const spend of block.spends()) {
-        if (processedSpends.has(spend.nullifier)) {
-          return { valid: false, reason: VerificationResultReason.DOUBLE_SPEND }
-        }
-
-        const verificationError = await this.verifySpend(
-          spend,
-          previousNotesSize,
-          previousNullifierSize,
-          tx,
-        )
+        const verificationError = await this.verifySpend(spend, previousNotesSize, tx)
         if (verificationError) {
           return { valid: false, reason: verificationError }
         }
-
-        processedSpends.add(spend.nullifier)
       }
 
       return { valid: true }
     })
   }
 
   /**
-   * Verify the block before connecting it to the main chain
+   * Verify the block does not contain any double spends before connecting it
    */
   async verifyBlockConnect(
     block: Block,
     tx?: IDatabaseTransaction,
   ): Promise<VerificationResult> {
-    if (
-      this.chain.consensus.isActive(this.chain.consensus.V1_DOUBLE_SPEND, block.header.sequence)
-    ) {
-      // Loop over all spends in the block and check that the nullifier has not previously been spent
-      const seen = new BufferSet()
-      const size = await this.chain.nullifiers.size(tx)
+    const seen = new BufferSet()
 
-      for (const spend of block.spends()) {
-        if (seen.has(spend.nullifier)) {
-          return { valid: false, reason: VerificationResultReason.DOUBLE_SPEND }
-        }
-
-        if (await this.chain.nullifiers.contained(spend.nullifier, size, tx)) {
-          return { valid: false, reason: VerificationResultReason.DOUBLE_SPEND }
-        }
+    for (const spend of block.spends()) {
+      if (seen.has(spend.nullifier)) {
+        return { valid: false, reason: VerificationResultReason.DOUBLE_SPEND }
+      }
 
-        seen.add(spend.nullifier)
+      if (await this.chain.nullifiers.contains(spend.nullifier, tx)) {
+        return { valid: false, reason: VerificationResultReason.DOUBLE_SPEND }
       }
+
+      seen.add(spend.nullifier)
     }
 
     return { valid: true }
   }
 
   /**
-   * Verify that the given spend was not in the nullifiers tree when it was the given size,
-   * and that the root of the notes tree is the one that is actually associated with the
+   * Verify that the root of the notes tree is the one that is actually associated with the
    * spend's spend root.
    *
    * @param spend the spend to be verified
    * @param notesSize the size of the notes tree
-   * @param nullifierSize the size of the nullifiers tree at which the spend must not exist
    * @param tx optional transaction context within which to check the spends.
-   * TODO as its expensive, this would be a good place for a cache/map of verified Spends
    */
   async verifySpend(
     spend: Spend,
     notesSize: number,
-    nullifierSize: number,
     tx?: IDatabaseTransaction,
   ): Promise<VerificationResultReason | undefined> {
-    if (await this.chain.nullifiers.contained(spend.nullifier, nullifierSize, tx)) {
-      return VerificationResultReason.DOUBLE_SPEND
-    }
-
     if (spend.size > notesSize) {
       return VerificationResultReason.NOTE_COMMITMENT_SIZE_TOO_LARGE
     }
```

### ironfish/src/testUtilities/matchers/blockchain.ts
```diff
@@ -50,10 +50,27 @@ async function toAddBlock(self: Blockchain, other: Block): Promise<jest.CustomMa
   return makeResult(true, `Expected to not add block at ${String(other.header.sequence)}`)
 }
 
+async function toAddDoubleSpendBlock(
+  self: Blockchain,
+  other: Block,
+): Promise<jest.CustomMatcherResult> {
+  // Mock nullifiers to allow creation of a double spend chain
+  const containsMock = jest.spyOn(self.nullifiers, 'contains').mockResolvedValue(false)
+  const result = await self.addBlock(other)
+  containsMock.mockRestore()
+
+  if (!result.isAdded) {
+    return makeResult(false, `Could not add block: ${String(result.reason)}`)
+  }
+
+  return makeResult(true, `Expected to not add block at ${String(other.header.sequence)}`)
+}
+
 expect.extend({
   toEqualHash: toEqualHash,
   toEqualNullifier: toEqualNullifier,
   toAddBlock: toAddBlock,
+  toAddDoubleSpendBlock: toAddDoubleSpendBlock,
 })
 
 declare global {
@@ -62,6 +79,7 @@ declare global {
       toEqualNullifier(other: Nullifier): R
       toEqualHash(other: BlockHash | null | undefined): R
       toAddBlock(block: Block): Promise<R>
+      toAddDoubleSpendBlock(block: Block): Promise<R>
     }
   }
 }
```
