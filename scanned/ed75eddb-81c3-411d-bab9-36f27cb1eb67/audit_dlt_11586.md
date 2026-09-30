# [?] fix: gosec vulnerabilities (#114)

## Summary
Severity: Unknown
Chain: Evmos
Component: evmos/evmos
Published: 2021-11-25
Source: https://github.com/evmos/evmos/commit/c3a601116c1f11d985073609ed7da1dfcab2f4cc
Type: security-commit

## Details
fix: gosec vulnerabilities (#114)

* Improvement(Evmos): Fix gosec vulnerabilities

* fix merge conflict in network.go

## Patch
### app/export.go
```diff
@@ -188,7 +188,9 @@ func (app *Evmos) prepForZeroHeightGenesis(ctx sdk.Context, jailAllowedAddrs []s
 		counter++
 	}
 
-	iter.Close()
+	if err := iter.Close(); err != nil {
+		return err
+	}
 
 	if _, err := app.StakingKeeper.ApplyAndReturnValidatorSetUpdates(ctx); err != nil {
 		return err
```

### cmd/evmosd/testnet.go
```diff
@@ -556,7 +556,10 @@ func startTestnet(cmd *cobra.Command, args startArgs) error {
 	}
 
 	cmd.Println("press the Enter Key to terminate")
-	fmt.Scanln() // wait for Enter Key
+	_, err = fmt.Scanln() // wait for Enter Key
+	if err != nil {
+		return err
+	}
 	testnet.Cleanup()
 
 	return nil
```

### x/intrarelayer/types/events.go
```diff
@@ -16,11 +16,11 @@ const (
 	EventTypeBurn                 = "burn"
 	EventTypeRegisterCoin         = "register_coin"
 	EventTypeRegisterERC20        = "register_erc20"
-	EventTypeToggleTokenRelay     = "toggle_token_relay" // nolint: gosec
+	EventTypeToggleTokenRelay     = "toggle_token_relay" // #nosec
 	EventTypeUpdateTokenPairERC20 = "update_token_pair_erc20"
 
 	AttributeKeyCosmosCoin = "cosmos_coin"
-	AttributeKeyERC20Token = "erc20_token" // nolint: gosec
+	AttributeKeyERC20Token = "erc20_token" // #nosec
 	AttributeKeyReceiver   = "receiver"
 
 	ERC20EventTransfer = "Transfer"
```

### x/intrarelayer/types/proposal.go
```diff
@@ -17,7 +17,7 @@ import (
 const (
 	ProposalTypeRegisterCoin         string = "RegisterCoin"
 	ProposalTypeRegisterERC20        string = "RegisterERC20"
-	ProposalTypeToggleTokenRelay     string = "ToggleTokenRelay" // nolint: gosec
+	ProposalTypeToggleTokenRelay     string = "ToggleTokenRelay" // #nosec
 	ProposalTypeUpdateTokenPairERC20 string = "UpdateTokenPairERC20"
 )
 
```
