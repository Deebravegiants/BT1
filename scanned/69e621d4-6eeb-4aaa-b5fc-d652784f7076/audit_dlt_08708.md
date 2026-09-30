# [?] Fixes deadlock when releasing lock in MaybeRunMaintenance

## Summary
Severity: Unknown
Chain: Arbitrum
Component: OffchainLabs/nitro
Published: 2025-07-21
Source: https://github.com/OffchainLabs/nitro/commit/fe3280acc8f7800222c832b99d7d565aa21cae62
Type: security-commit

## Details
Fixes deadlock when releasing lock in MaybeRunMaintenance

## Patch
### arbnode/maintenance.go
```diff
@@ -105,7 +105,10 @@ func (mr *MaintenanceRunner) MaybeRunMaintenance(ctx context.Context) time.Durat
 		return config.CheckInterval
 	}
 	defer func() {
-		release <- struct{}{}
+		select {
+		case release <- struct{}{}:
+		case <-ctx.Done():
+		}
 	}()
 
 	log.Info("Attempting avoiding lockout and handing off")
```
