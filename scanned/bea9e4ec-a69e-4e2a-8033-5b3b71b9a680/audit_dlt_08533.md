# [?] tests: fix TestNodeSetCatchpointCatchupMode data race (#6574)

## Summary
Severity: Unknown
Chain: Algorand
Component: algorand/go-algorand
Published: 2026-03-10
Source: https://github.com/algorand/go-algorand/commit/72220dd949764b020d184c7f22cedcad0b98c8c5
Type: security-commit

## Details
tests: fix TestNodeSetCatchpointCatchupMode data race (#6574)

## Patch
### node/node.go
```diff
@@ -1247,7 +1247,7 @@ func (node *AlgorandFullNode) AbortCatchup(catchpoint string) error {
 // channel which contains the updated node context. This function need to work asynchronously so that the caller could
 // detect and handle the use case where the node is being shut down while we're switching to/from catchup mode without
 // deadlocking on the shared node mutex.
-func (node *AlgorandFullNode) SetCatchpointCatchupMode(catchpointCatchupMode bool) (outCtxCh <-chan context.Context) {
+func (node *AlgorandFullNode) SetCatchpointCatchupMode(enable bool) (outCtxCh <-chan context.Context) {
 	// create a non-buffered channel to return the newly created context. The fact that it's non-buffered here
 	// is important, as it allows us to synchronize the "receiving" of the new context before canceling of the previous
 	// one.
@@ -1262,7 +1262,7 @@ func (node *AlgorandFullNode) SetCatchpointCatchupMode(catchpointCatchupMode boo
 			node.mu.Unlock()
 			return
 		}
-		if catchpointCatchupMode {
+		if enable {
 			// stop..
 			defer func() {
 				node.mu.Unlock()
```

### node/node_test.go
```diff
@@ -1181,6 +1181,10 @@ func TestNodeSetCatchpointCatchupMode(t *testing.T) {
 			// "start" catchpoint catchup => close services
 			outCh := n.SetCatchpointCatchupMode(true)
 			<-outCh
+			// make sure SetCatchpointCatchupMode' goroutine has completely finished
+			// to prevent data race on stop/start services
+			n.waitMonitoringRoutines()
+
 			// "stop" catchpoint catchup => resume services
 			outCh = n.SetCatchpointCatchupMode(false)
 			<-outCh
```
