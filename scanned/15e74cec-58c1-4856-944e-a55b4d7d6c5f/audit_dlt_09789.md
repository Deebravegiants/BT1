# [?] fix nil host panic in bootnode shutdown

## Summary
Severity: Unknown
Chain: Harmony
Component: harmony-one/harmony
Published: 2026-02-12
Source: https://github.com/harmony-one/harmony/commit/83edb47378358bb80f6499ae8f2c34bae824cf01
Type: security-commit

## Details
fix nil host panic in bootnode shutdown

## Patch
### node/boot/bootnode.go
```diff
@@ -83,8 +83,10 @@ func (bootnode *BootNode) ShutDown() {
 	}
 
 	utils.Logger().Info().Msg("stopping boot host")
-	if err := bootnode.host.Close(); err != nil {
-		utils.Logger().Error().Err(err).Msg("failed to stop boot p2p host")
+	if bootnode.host != nil {
+		if err := bootnode.host.Close(); err != nil {
+			utils.Logger().Error().Err(err).Msg("failed to stop boot p2p host")
+		}
 	}
 
 	const msg = "Successfully shut down boot!\n"
```
