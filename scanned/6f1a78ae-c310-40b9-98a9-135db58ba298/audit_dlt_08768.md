# [?] light: fixed data race in TestTxPool

## Summary
Severity: Unknown
Chain: Scroll
Component: scroll-tech/go-ethereum
Published: 2017-01-06
Source: https://github.com/scroll-tech/go-ethereum/commit/66979aa468b6329aabf49542bd3db14e59010c20
Type: security-commit

## Details
light: fixed data race in TestTxPool

## Patch
### light/txpool_test.go
```diff
@@ -32,20 +32,22 @@ import (
 )
 
 type testTxRelay struct {
-	send, nhMined, nhRollback, discard int
+	send, discard, mined chan int
 }
 
 func (self *testTxRelay) Send(txs types.Transactions) {
-	self.send = len(txs)
+	self.send <- len(txs)
 }
 
 func (self *testTxRelay) NewHead(head common.Hash, mined []common.Hash, rollback []common.Hash) {
-	self.nhMined = len(mined)
-	self.nhRollback = len(rollback)
+	m := len(mined)
+	if m != 0 {
+		self.mined <- m
+	}
 }
 
 func (self *testTxRelay) Discard(hashes []common.Hash) {
-	self.discard = len(hashes)
+	self.discard <- len(hashes)
 }
 
 const poolTestTxs = 1000
@@ -94,7 +96,11 @@ func TestTxPool(t *testing.T) {
 	}
 
 	odr := &testOdr{sdb: sdb, ldb: ldb}
-	relay := &testTxRelay{}
+	relay := &testTxRelay{
+		send:    make(chan int, 1),
+		discard: make(chan int, 1),
+		mined:   make(chan int, 1),
+	}
 	lightchain, _ := NewLightChain(odr, testChainConfig(), pow, evmux)
 	lightchain.SetValidator(bproc{})
 	txPermanent = 50
@@ -106,36 +112,33 @@ func TestTxPool(t *testing.T) {
 		s := sentTx(i - 1)
 		e := sentTx(i)
 		for i := s; i < e; i++ {
-			relay.send = 0
 			pool.Add(ctx, testTx[i])
-			got := relay.send
+			got := <-relay.send
 			exp := 1
 			if got != exp {
 				t.Errorf("relay.Send expected len = %d, got %d", exp, got)
 			}
 		}
 
-		relay.nhMined = 0
-		relay.nhRollback = 0
-		relay.discard = 0
 		if _, err := lightchain.InsertHeaderChain([]*types.Header{block.Header()}, 1); err != nil {
 			panic(err)
 		}
-		time.Sleep(time.Millisecond * 30)
 
-		got := relay.nhMined
+		got := <-relay.mined
 		exp := minedTx(i) - minedTx(i-1)
 		if got != exp {
 			t.Errorf("relay.NewHead expected len(mined) = %d, got %d", exp, got)
 		}
 
-		got = relay.discard
 		exp = 0
 		if i > int(txPermanent)+1 {
 			exp = minedTx(i-int(txPermanent)-1) - minedTx(i-int(txPermanent)-2)
 		}
-		if got != exp {
-			t.Errorf("relay.Discard expected len = %d, got %d", exp, got)
+		if exp != 0 {
+			got = <-relay.discard
+			if got != exp {
+				t.Errorf("relay.Discard expected len = %d, got %d", exp, got)
+			}
 		}
 	}
 }
```
