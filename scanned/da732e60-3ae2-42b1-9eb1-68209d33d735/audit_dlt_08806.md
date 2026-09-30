# [?] fix panic NewStackTrie (#3146)

## Summary
Severity: Unknown
Chain: Polygon zkEVM
Component: 0xPolygon/zkevm-node
Published: 2024-01-25
Source: https://github.com/0xPolygon/zkevm-node/commit/18251645a592c3147a421ac53a796c42a89af100
Type: security-commit

## Details
fix panic NewStackTrie (#3146)

## Patch
### state/transaction.go
```diff
@@ -248,7 +248,8 @@ func (s *State) StoreL2Block(ctx context.Context, batchNumber uint64, l2Block *P
 	}
 
 	// Create block to be able to calculate its hash
-	block := NewL2Block(l2Header, transactions, []*L2Header{}, receipts, &trie.StackTrie{})
+	st := trie.NewStackTrie(nil)
+	block := NewL2Block(l2Header, transactions, []*L2Header{}, receipts, st)
 	block.ReceivedAt = time.Unix(int64(l2Block.Timestamp), 0)
 
 	for _, receipt := range receipts {
```
