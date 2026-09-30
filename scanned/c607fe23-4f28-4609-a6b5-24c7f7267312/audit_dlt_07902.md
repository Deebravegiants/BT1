# [?] fix: discovery AyncFilter deadlock on shutdown (#3347)

## Summary
Severity: Unknown
Chain: BNB Chain
Component: bnb-chain/bsc
Published: 2025-09-10
Source: https://github.com/bnb-chain/bsc/commit/da459f4a33fce66c57e289a9190d05e96940c3ec
Type: security-commit

## Details
fix: discovery AyncFilter deadlock on shutdown (#3347)

## Patch
### p2p/enode/iter.go
```diff
@@ -180,7 +180,7 @@ type AsyncFilterFunc func(context.Context, *Node) *Node
 func AsyncFilter(it Iterator, check AsyncFilterFunc, workers int) Iterator {
 	f := &asyncFilterIter{
 		it:     ensureSourceIter(it),
-		slots:  make(chan struct{}, workers+1),
+		slots:  make(chan struct{}, workers+1), // extra 1 slot to make sure all the goroutines can be completed
 		passed: make(chan iteratorItem),
 	}
 	for range cap(f.slots) {
@@ -195,6 +195,9 @@ func AsyncFilter(it Iterator, check AsyncFilterFunc, workers int) Iterator {
 			return
 		case <-f.slots:
 		}
+		defer func() {
+			f.slots <- struct{}{} // the iterator has ended
+		}()
 		// read from the iterator and start checking nodes in parallel
 		// when a node is checked, it will be sent to the passed channel
 		// and the slot will be released
@@ -203,7 +206,11 @@ func AsyncFilter(it Iterator, check AsyncFilterFunc, workers int) Iterator {
 			nodeSource := f.it.NodeSource()
 
 			// check the node async, in a separate goroutine
-			<-f.slots
+			select {
+			case <-ctx.Done():
+				return
+			case <-f.slots:
+			}
 			go func() {
 				if nn := check(ctx, node); nn != nil {
 					item := iteratorItem{nn, nodeSource}
@@ -215,8 +222,6 @@ func AsyncFilter(it Iterator, check AsyncFilterFunc, workers int) Iterator {
 				f.slots <- struct{}{}
 			}()
 		}
-		// the iterator has ended
-		f.slots <- struct{}{}
 	}()
 
 	return f
```
