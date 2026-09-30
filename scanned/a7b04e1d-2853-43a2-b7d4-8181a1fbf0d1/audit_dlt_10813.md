# [?] avoid returning error, as it cause consensus failure

## Summary
Severity: Unknown
Chain: Secret
Component: scrtlabs/SecretNetwork
Published: 2025-04-14
Source: https://github.com/scrtlabs/SecretNetwork/commit/dee996bfe0f55070b79ba722ddfe66dda3f4ed80
Type: security-commit

## Details
avoid returning error, as it cause consensus failure

## Patch
### x/compute/internal/keeper/keeper.go
```diff
@@ -1126,18 +1126,6 @@ func (k Keeper) GetScheduledMsgs(ctx sdk.Context, execution_stage crontypes.Exec
 		txBytesList = append(txBytesList, txBytes)
 		executeMsgList = append(executeMsgList, executeMsg)
 
-		// Execute the contract.
-		// _, err = k.Execute(cacheCtx, executeMsg.Contract, executeMsg.Sender, executeMsg.Msg, executeMsg.SentFunds, executeMsg.CallbackSig, wasmTypes.HandleTypeExecute)
-		// if err != nil {
-		// 	ctx.Logger().Info("executeSchedule: failed to execute contract msg",
-		// 		"schedule_name", ExecuteScheduledMsgs.Name,
-		// 		"msg_idx", idx,
-		// 		"msg_contract", msg.Contract,
-		// 		"msg", msg.Msg,
-		// 		"error", err,
-		// 	)
-		// 	return err
-		// }
 	}
 
 	// Commit changes if all messages were executed successfully.
```

### x/compute/module.go
```diff
@@ -203,12 +203,11 @@ func (am AppModule) BeginBlock(c context.Context) error {
 		for idx, msg := range execCronMsgs {
 			fmt.Printf("idx, msg: %+v %+v\n", idx, msg)
 			ctx = ctx.WithTxBytes(bytesCronMsgs[idx])
-			res, err := am.keeper.Execute(ctx, msg.Contract, msg.Sender, msg.Msg, msg.SentFunds, msg.CallbackSig, wasmtypes.HandleTypeExecute)
+			_, err := am.keeper.Execute(ctx, msg.Contract, msg.Sender, msg.Msg, msg.SentFunds, msg.CallbackSig, wasmtypes.HandleTypeExecute)
 			if err != nil {
 				ctx.Logger().Error("Failed to execute cron message", "error", err)
-				return err
+				// return err
 			}
-			fmt.Printf("res: %+v\n", res)
 		}
 
 		fmt.Printf("setRandomSeed\n")
```
