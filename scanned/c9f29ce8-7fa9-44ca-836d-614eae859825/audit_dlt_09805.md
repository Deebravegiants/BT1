# [?] Fix possible panic.

## Summary
Severity: Unknown
Chain: Harmony
Component: harmony-one/harmony
Published: 2023-03-21
Source: https://github.com/harmony-one/harmony/commit/1a70d5eb66cdbf8a23791806b71a323eed320085
Type: security-commit

## Details
Fix possible panic.

## Patch
### core/blockchain_stub.go
```diff
@@ -141,10 +141,6 @@ func (a Stub) Config() *params.ChainConfig {
 	return nil
 }
 
-func (a Stub) Engine() engine.Engine {
-	return nil
-}
-
 func (a Stub) SubscribeRemovedLogsEvent(ch chan<- RemovedLogsEvent) event.Subscription {
 	return nil
 }
```

### core/epochchain.go
```diff
@@ -128,7 +128,7 @@ func (bc *EpochChain) InsertChain(blocks types.Blocks, _ bool) (int, error) {
 		}
 
 		// Signature validation.
-		err = bc.Engine().VerifyHeaderSignature(bc, block.Header(), sig, bitmap)
+		err = chain.Engine().VerifyHeaderSignature(bc, block.Header(), sig, bitmap)
 		if err != nil {
 			return i, errors.Wrap(err, "failed signature validation")
 		}
```
