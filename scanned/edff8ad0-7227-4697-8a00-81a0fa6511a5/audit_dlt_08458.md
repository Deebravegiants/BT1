# [?] fix(core): Fix log that panics if !ok (#1927)

## Summary
Severity: Unknown
Chain: Celestia
Component: celestiaorg/celestia-node
Published: 2023-03-17
Source: https://github.com/celestiaorg/celestia-node/commit/c8a40bc701bcdc825fa5bb02ab1adae8a7ecacb8
Type: security-commit

## Details
fix(core): Fix log that panics if !ok (#1927)

Self explanatory. :(

## Patch
### core/listener.go
```diff
@@ -80,10 +80,10 @@ func (cl *Listener) listen(ctx context.Context, sub <-chan *types.Block) {
 	for {
 		select {
 		case b, ok := <-sub:
-			log.Debugw("listener: new block from core", "height", b.Height)
 			if !ok {
 				return
 			}
+			log.Debugw("listener: new block from core", "height", b.Height)
 
 			syncing, err := cl.fetcher.IsSyncing(ctx)
 			if err != nil {
```
