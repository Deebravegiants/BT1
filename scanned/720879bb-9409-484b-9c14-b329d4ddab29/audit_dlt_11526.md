# [?] fix(testnode): return error instead of panicking on gRPC port conflict (#6603)

## Summary
Severity: Unknown
Chain: Celestia
Component: celestiaorg/celestia-app
Published: 2026-02-18
Source: https://github.com/celestiaorg/celestia-app/commit/493251a2e1e59fe1a2ff120658ab0c54016e8101
Type: security-commit

## Details
fix(testnode): return error instead of panicking on gRPC port conflict (#6603)

## Summary
- `StartGRPCServer` in `test/util/testnode/rpc_client.go` panics when
the gRPC port is already in use, crashing the entire test process
instead
  of allowing callers to handle the error
- Replace `panic(err)` with an error channel + timeout pattern, matching
the existing `StartAPIServer` implementation
- This allows downstream test code (e.g. in celestia-node) to catch port
conflicts and retry with fresh ports

  Observed panic in CI:
panic: failed to listen on address 127.0.0.1:51126: listen tcp
127.0.0.1:51126: bind: address already in use

  goroutine 309782 [running]:

github.com/celestiaorg/celestia-app/v7/test/util/testnode.StartGRPCServer.func2()
      celestia-app/v7@v7.0.1-arabica/test/util/testnode/rpc_client.go:87


Ref:
https://github.com/celestiaorg/celestia-node/actions/runs/22147014078/job/64033254886?pr=4787#step:4:405

Co-authored-by: Rootul P <rootulp@gmail.com>

## Patch
### test/util/testnode/rpc_client.go
```diff
@@ -81,13 +81,20 @@ func StartGRPCServer(logger log.Logger, app srvtypes.Application, appCfg *srvcon
 		grpcLogger = log.NewLogger(os.Stdout)
 	}
 
+	errCh := make(chan error, 1)
 	go func() {
-		// StartGRPCServer is a blocking function, we need to run it in a go routine.
-		if err := srvgrpc.StartGRPCServer(cctx.goContext, grpcLogger, appCfg.GRPC, grpcSrv); err != nil {
-			panic(err)
-		}
+		// StartGRPCServer is a blocking function, we need to run it in a goroutine.
+		errCh <- srvgrpc.StartGRPCServer(cctx.goContext, grpcLogger, appCfg.GRPC, grpcSrv)
 	}()
 
+	// Give the server a moment to fail fast on port conflicts before proceeding.
+	select {
+	case err := <-errCh:
+		return nil, Context{}, emptycleanup, err
+	case <-time.After(500 * time.Millisecond):
+		// assume server started successfully (same pattern as StartAPIServer)
+	}
+
 	nodeGRPCAddr := strings.Replace(appCfg.GRPC.Address, "0.0.0.0", "localhost", 1)
 	conn, err := grpc.NewClient(
 		nodeGRPCAddr,
```
