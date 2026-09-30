# [?] fix(sync): Dont panic on startup if block not found or err (#261)

## Summary
Severity: Unknown
Chain: Berachain
Component: berachain/beacon-kit
Published: 2024-02-22
Source: https://github.com/berachain/beacon-kit/commit/1650da3d1fa96be4bdc993cdde073ae93af77cd7
Type: security-commit

## Details
fix(sync): Dont panic on startup if block not found or err (#261)

* fix(sync): Dont panic on startup if block not found or err

* remove comment

* improve comment

## Patch
### beacon/sync/service.go
```diff
@@ -38,6 +38,10 @@ import (
 	"github.com/itsdevbear/bolaris/runtime/service"
 )
 
+// syncCheckInterval is the interval at which the sync status is checked
+// during WaitForExecutionClientSync.
+const syncCheckInterval = 3 * time.Second
+
 // Service is responsible for tracking the synchornization status
 // of both the beacon and execution chains.
 type Service struct {
@@ -197,21 +201,15 @@ func (s *Service) WaitForExecutionClientSync(ctx context.Context) error {
 		elLatestFinalizedHeader, err := s.ethClient.HeaderByNumber(
 			ctx, rpcFinalizedBlockNumber,
 		)
-		// TODO: properly handle if the EL loses connection, right now
-		// this function will just panic. This function should stay alive
-		// during EL node restarts / disconnections.
 		if err != nil {
-			// TODO: different execution clients are going to handle this
-			// differently, we should probably have a way to handle this
-			// more gracefully.
-			if err.Error() == "Unknown block" || err.Error() == "unknown block" {
-				// If the block is unknown, we can just continue and try again.
-				// We set elLatestFinalizedHeader to an empty Header to prevent
-				// a nil ptr dereference further down.
-				elLatestFinalizedHeader = &ethtypes.Header{}
-			} else {
-				return err
-			}
+			// If the block is unknown or the call errors, we can just continue and try again.
+			// We set elLatestFinalizedHeader to an empty Header to prevent
+			// a nil ptr dereference further down.
+			elLatestFinalizedHeader = &ethtypes.Header{}
+			s.Logger().Warn(
+				"failed to get latest finalized header from execution client",
+				"error", err,
+			)
 		}
 
 		s.Logger().Info(
@@ -229,11 +227,11 @@ func (s *Service) WaitForExecutionClientSync(ctx context.Context) error {
 		select {
 		case <-ctx.Done():
 			return ctx.Err()
-		case <-time.After(3 * time.Second): //nolint:gomnd // 3 seconds is fine.
+		case <-time.After(syncCheckInterval):
 			continue
 		}
 	}
 
-	s.Logger().Info("execution client is synced with consensus client 🎉")
+	s.Logger().Info("execution client is synchronized with consensus client 🎉")
 	return nil
 }
```
