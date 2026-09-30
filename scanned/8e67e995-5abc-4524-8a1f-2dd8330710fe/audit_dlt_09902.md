# [?] Change double spend test to use non-native asset (#3126)

## Summary
Severity: Unknown
Chain: Iron Fish
Component: iron-fish/ironfish
Published: 2023-01-25
Source: https://github.com/iron-fish/ironfish/commit/7d9b3b05d5c5c58e10fe8015f0c71860de262bdc
Type: security-commit

## Details
Change double spend test to use non-native asset (#3126)

## Patch
### ironfish/src/blockchain/blockchain.test.ts
```diff
@@ -1362,13 +1362,31 @@ describe('Blockchain', () => {
         const { node } = await nodeTest.createSetup()
         const account = await useAccountFixture(node.wallet)
 
-        const mined = await useMinerBlockFixture(node.chain, undefined, account)
-        await expect(node.chain).toAddBlock(mined)
+        const asset = new Asset(account.spendingKey, 'mint-asset', 'metadata')
+        const mintValue = BigInt(10)
+        const assetId = asset.id()
+
+        const block = await useMintBlockFixture({
+          node: node,
+          account: account,
+          sequence: 2,
+          asset,
+          value: mintValue,
+        })
+        await expect(node.chain).toAddBlock(block)
         await node.wallet.updateHead()
 
+        // Verify Node A has the asset
+        const record = await node.chain.assets.get(assetId)
+        Assert.isNotUndefined(record)
+        expect(record).toMatchObject({
+          createdTransactionHash: block.transactions[1].hash(),
+          supply: mintValue,
+        })
+
         const doubleSpend = await useBlockFixture(node.chain, async () => {
           // The note to double spend
-          const note = await account.getDecryptedNote(mined.transactions[0].getNote(0).hash())
+          const note = await account.getDecryptedNote(block.transactions[1].getNote(0).hash())
 
           Assert.isNotUndefined(note)
           Assert.isNotNull(note.index)
@@ -1378,7 +1396,7 @@ describe('Blockchain', () => {
           const rawBurn = new RawTransaction()
           rawBurn.spendingKey = account.spendingKey
           rawBurn.spends = [{ note: note.note, witness }]
-          rawBurn.burns = [{ assetId: Asset.nativeId(), value: BigInt(2) }]
+          rawBurn.burns = [{ assetId, value: BigInt(2) }]
 
           const rawSend = new RawTransaction()
           rawSend.spendingKey = account.spendingKey
@@ -1390,7 +1408,7 @@ describe('Blockchain', () => {
                   account.publicAddress,
                   3n,
                   '',
-                  Asset.nativeId(),
+                  assetId,
                   account.publicAddress,
                 ).serialize(),
               ),
```
