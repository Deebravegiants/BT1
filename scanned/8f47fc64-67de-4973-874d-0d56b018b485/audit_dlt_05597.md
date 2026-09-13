# [?] p2p/enode: fix discovery AyncFilter deadlock on shutdown (#32572)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2025-10-02
Source: https://github.com/ethereum/go-ethereum/commit/f0dc47aae393abe0bb7b084345daf9108ad8897a
Type: security-commit

## Details
p2p/enode: fix discovery AyncFilter deadlock on shutdown (#32572)

Description:
We found a occasionally node hang issue on BSC, I think Geth may
also have the issue, so pick the fix patch here.
The fix on BSC repo: https://github.com/bnb-chain/bsc/pull/3347

When the hang occurs, there are two routines stuck.
- routine 1: AsyncFilter(...)
On node start, it will run part of the DiscoveryV4 protocol, which could
take considerable time, here is its hang callstack:
```
goroutine 9711 [chan receive]:  // this routine was stuck on read channel: `<-f.slots`
github.com/ethereum/go-ethereum/p2p/enode.AsyncFilter.func1()
	github.com/ethereum/go-ethereum/p2p/enode/iter.go:206 +0x125
created by github.com/ethereum/go-ethereum/p2p/enode.AsyncFilter in goroutine 1
	github.com/ethereum/go-ethereum/p2p/enode/iter.go:192 +0x205

```

- Routine 2: Node Stop
It is the main routine to shutdown the process, but it got stuck when it
tries to shutdown the discovery components, as it tries to drain the
channel of `<-f.slots`, but the extra 1 slot will never have chance to
be resumed.
```
goroutine 11796 [chan receive]: 
github.com/ethereum/go-ethereum/p2p/enode.(*asyncFilterIter).Close.func1()
	github.com/ethereum/go-ethereum/p2p/enode/iter.go:248 +0x5c
sync.(*Once).doSlow(0xc032a97cb8?, 0xc032a97d18?)
	sync/once.go:78 +0xab
sync.(*Once).Do(...)
	sync/once.go:69
github.com/ethereum/go-ethereum/p2p/enode.(*asyncFilterIter).Close(0xc092ff8d00?)
	github.com/ethereum/go-ethereum/p2p/enode/iter.go:244 +0x36
github.com/ethereum/go-ethereum/p2p/enode.(*bufferIter).Close.func1()
	github.com/ethereum/go-ethereum/p2p/enode/iter.go:299 +0x24
sync.(*Once).doSlow(0x11a175f?, 0x2bfe63e?)
	sync/once.go:78 +0xab
sync.(*Once).Do(...)
	sync/once.go:69
github.com/ethereum/go-ethereum/p2p/enode.(*bufferIter).Close(0x30?)
	github.com/ethereum/go-ethereum/p2p/enode/iter.go:298 +0x36
github.com/ethereum/go-ethereum/p2p/enode.(*FairMix).Close(0xc0004bfea0)
	github.com/ethereum/go-ethereum/p2p/enode/iter.go:379 +0xb7
github.com/ethereum/go-ethereum/eth.(*Ethereum).Stop(0xc000997b00)
	github.com/ethereum/go-ethereum/eth/backend.go:960 +0x4a
github.com/ethereum/go-ethereum/node.(*Node).stopServices(0xc0001362a0, {0xc012e16330, 0x1, 0xc000111410?})
	github.com/ethereum/go-ethereum/node/node.go:333 +0xb3
github.com/ethereum/go-ethereum/node.(*Node).Close(0xc0001362a0)
	github.com/ethereum/go-ethereum/node/node.go:263 +0x167
created by github.com/ethereum/go-ethereum/cmd/utils.StartNode.func1.1 in goroutine 9729
	github.com/ethereum/go-ethereum/cmd/utils/cmd.go:101 +0x78
```

The rootcause of the hang is caused by the extra 1 slot, which was
designed to make sure the routines in `AsyncFilter(...)` can be
finished. This PR fixes it by making sure the extra 1 shot can always be
resumed when node shutdown.

### p2p/enode/iter.go
```diff
@@ -178,7 +178,7 @@ type AsyncFilterFunc func(context.Context, *Node) *Node
 func AsyncFilter(it Iterator, check AsyncFilterFunc, workers int) Iterator {
 	f := &asyncFilterIter{
 		it:     ensureSourceIter(it),
-		slots:  make(chan struct{}, workers+1),
+		slots:  make(chan struct{}, workers+1), // extra 1 slot to make sure all the goroutines can be completed
 		passed: make(chan iteratorItem),
 	}
 	for range cap(f.slots) {
@@ -193,6 +193,9 @@ func AsyncFilter(it Iterator, check AsyncFilterFunc, workers int) Iterator {
 			return
 		case <-f.slots:
 		}
+		defer func() {
+			f.slots <- struct{}{} // the iterator has ended
+		}()
 		// read from the iterator and start checking nodes in parallel
 		// when a node is checked, it will be sent to the passed channel
 		// and the slot will be released
@@ -201,7 +204,11 @@ func AsyncFilter(it Iterator, check AsyncFilterFunc, workers int) Iterator {
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
@@ -213,8 +220,6 @@ func AsyncFilter(it Iterator, check AsyncFilterFunc, workers int) Iterator {
 				f.slots <- struct{}{}
 			}()
 		}
-		// the iterator has ended
-		f.slots <- struct{}{}
 	}()
 
 	return f
```
