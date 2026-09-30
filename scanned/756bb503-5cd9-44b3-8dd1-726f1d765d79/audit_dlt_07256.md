# [?] abci/client: fix DATA RACE in gRPC client (#3798)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cometbft/cometbft
Published: 2019-07-17
Source: https://github.com/cometbft/cometbft/commit/1844bff6133c6684077ec914bf425566c33bf51b
Type: security-commit

## Details
abci/client: fix DATA RACE in gRPC client (#3798)

* Remove go func {}()

closes #357

- Remove go func(){}() that caused race condiditon

- To reproduce
	- add -race in make file to `install_abci`
	- Remove `CGO_ENABLED=0` & add -race to `install`

Signed-off-by: Marko Baricevic <marbar3778@yahoo.com>

* remove -race

* fix data race

also, reorder callbacks similarly to socket client

## Patch
### abci/client/grpc_client.go
```diff
@@ -228,18 +228,22 @@ func (cli *grpcClient) finishAsyncCall(req *types.Request, res *types.Response)
 	reqres.Done()         // Release waiters
 	reqres.SetDone()      // so reqRes.SetCallback will run the callback
 
-	// go routine for callbacks
+	// goroutine for callbacks
 	go func() {
-		// Notify reqRes listener if set
-		if cb := reqres.GetCallback(); cb != nil {
-			cb(res)
-		}
+		cli.mtx.Lock()
+		defer cli.mtx.Unlock()
 
 		// Notify client listener if set
 		if cli.resCb != nil {
 			cli.resCb(reqres.Request, res)
 		}
+
+		// Notify reqRes listener if set
+		if cb := reqres.GetCallback(); cb != nil {
+			cb(res)
+		}
 	}()
+
 	return reqres
 }
 
```
