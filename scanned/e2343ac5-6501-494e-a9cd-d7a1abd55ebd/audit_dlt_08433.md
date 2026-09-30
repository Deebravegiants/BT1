# [?] Merge pull request from GHSA-3v7p-4x7p-4rx7

## Summary
Severity: Unknown
Chain: Cosmos
Component: cosmos/ibc-go
Published: 2023-05-25
Source: https://github.com/cosmos/ibc-go/commit/4973957900d70969d99371e6ed24c47400f5abe6
Type: security-commit

## Details
Merge pull request from GHSA-3v7p-4x7p-4rx7

Co-authored-by: Carlos Rodriguez <carlos@interchain.io>

## Patch
### modules/core/keeper/msg_server.go
```diff
@@ -457,10 +457,6 @@ func (k Keeper) RecvPacket(goCtx context.Context, msg *channeltypes.MsgRecvPacke
 	if ack == nil || ack.Success() {
 		// write application state changes for asynchronous and successful acknowledgements
 		writeFn()
-	} else {
-		// NOTE: The context returned by CacheContext() refers to a new EventManager, so it needs to explicitly set events to the original context.
-		// Events should still be emitted from failed acks and asynchronous acks
-		ctx.EventManager().EmitEvents(cacheCtx.EventManager().Events())
 	}
 
 	// Set packet acknowledgement only if the acknowledgement is not nil.
```
