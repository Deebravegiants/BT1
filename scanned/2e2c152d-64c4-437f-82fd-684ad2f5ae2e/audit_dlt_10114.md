# [?] fix a crash in `OnGetDataMessageReceived`

## Summary
Severity: Unknown
Chain: Neo
Component: neo-project/neo
Published: 2018-09-09
Source: https://github.com/neo-project/neo/commit/00bfe73a38069d6a3b32933eafc41b14f727a874
Type: security-commit

## Details
fix a crash in `OnGetDataMessageReceived`

## Patch
### neo/Network/RemoteNode.cs
```diff
@@ -179,13 +179,13 @@ private void OnGetDataMessageReceived(InvPayload payload)
                             inventory = LocalNode.GetTransaction(hash);
                         if (inventory == null && Blockchain.Default != null)
                             inventory = Blockchain.Default.GetTransaction(hash);
-                        if (inventory != null)
+                        if (inventory is Transaction)
                             EnqueueMessage("tx", inventory);
                         break;
                     case InventoryType.Block:
                         if (inventory == null && Blockchain.Default != null)
                             inventory = Blockchain.Default.GetBlock(hash);
-                        if (inventory != null)
+                        if (inventory is Block block)
                         {
                             BloomFilter filter = bloom_filter;
                             if (filter == null)
@@ -194,7 +194,6 @@ private void OnGetDataMessageReceived(InvPayload payload)
                             }
                             else
                             {
-                                Block block = (Block)inventory;
                                 BitArray flags = new BitArray(block.Transactions.Select(p => TestFilter(filter, p)).ToArray());
                                 EnqueueMessage("merkleblock", MerkleBlockPayload.Create(block, flags));
                             }
```
