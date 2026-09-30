# [?] fix: cli: correctly return error panic-less-ly

## Summary
Severity: Unknown
Chain: Filecoin
Component: filecoin-project/lotus
Published: 2022-11-22
Source: https://github.com/filecoin-project/lotus/commit/610a3eee5dc3baf353c1211a72590f4ec0f1d1d4
Type: security-commit

## Details
fix: cli: correctly return error panic-less-ly

## Patch
### cmd/lotus-miner/actor.go
```diff
@@ -290,7 +290,7 @@ var actorWithdrawCmd = &cli.Command{
 		// wait for it to get mined into a block
 		wait, err := api.StateWaitMsg(ctx, res, uint64(cctx.Int("confidence")))
 		if err != nil {
-			return xerrors.Errorf("Timeout waiting for withdrawal message %s", wait.Message)
+			return xerrors.Errorf("Timeout waiting for withdrawal message %s", res)
 		}
 
 		if wait.Receipt.ExitCode.IsError() {
```
