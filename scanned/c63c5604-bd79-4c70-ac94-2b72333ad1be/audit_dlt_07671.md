# [?] rpcdaemon: remove check to avoid panic when access to Debug() method of KV remote (#15933)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2025-07-05
Source: https://github.com/erigontech/erigon/commit/91aba48801a74a9f9f80ee690a3f60f9ee051b44
Type: security-commit

## Details
rpcdaemon: remove check to avoid panic when access to Debug() method of KV remote (#15933)

remove same check on 3.0

fixes #15632

## Patch
### rpc/rpchelper/helper.go
```diff
@@ -169,9 +169,10 @@ func CreateHistoryStateReader(tx kv.TemporalTx, blockNumber uint64, txnIndex int
 		return nil, err
 	}
 	txNum := uint64(int(minTxNum) + txnIndex + /* 1 system txNum in beginning of block */ 1)
-	if txNum < r.StateHistoryStartFrom() {
-		return r, state.PrunedError
-	}
+
+	//if txNum < r.StateHistoryStartFrom() {
+	//	return r, state.PrunedError
+	//}
 	r.SetTxNum(txNum)
 	return r, nil
 }
```
