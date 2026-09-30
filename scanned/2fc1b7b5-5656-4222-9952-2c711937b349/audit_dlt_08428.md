# [?] fix possible mempool deadlock

## Summary
Severity: Unknown
Chain: Cosmos
Component: cometbft/cometbft
Published: 2018-06-02
Source: https://github.com/cometbft/cometbft/commit/98b0c51b5ff339a12999dc9345a2b2df3f15d944
Type: security-commit

## Details
fix possible mempool deadlock

## Patch
### mempool/mempool.go
```diff
@@ -72,8 +72,8 @@ type Mempool struct {
 	rechecking           int32           // for re-checking filtered txs on Update()
 	recheckCursor        *clist.CElement // next expected response
 	recheckEnd           *clist.CElement // re-checking stops here
-	notifiedTxsAvailable bool            // true if fired on txsAvailable for this height
-	txsAvailable         chan int64      // fires the next height once for each height, when the mempool is not empty
+	notifiedTxsAvailable bool
+	txsAvailable         chan int64 // fires the next height once for each height, when the mempool is not empty
 
 	// Keep a cache of already-seen txs.
 	// This reduces the pressure on the proxyApp.
@@ -328,8 +328,12 @@ func (mem *Mempool) notifyTxsAvailable() {
 		panic("notified txs available but mempool is empty!")
 	}
 	if mem.txsAvailable != nil && !mem.notifiedTxsAvailable {
+		select {
+		case mem.txsAvailable <- mem.height + 1:
+		default:
+		}
+
 		mem.notifiedTxsAvailable = true
-		mem.txsAvailable <- mem.height + 1
 	}
 }
 
```
