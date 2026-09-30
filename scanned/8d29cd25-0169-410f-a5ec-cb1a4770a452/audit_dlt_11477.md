# [?] Merge PR #701: Fix data race in getting transfer message signers

## Summary
Severity: Unknown
Chain: Cosmos
Component: cosmos/relayer
Published: 2022-04-12
Source: https://github.com/cosmos/relayer/commit/12f4c8c2236c5b26e071d37fcdef22c7329988b0
Type: security-commit

## Details
Merge PR #701: Fix data race in getting transfer message signers

This data race can occur when logging successful transactions. The
default path involves a potentially concurrent map access inside the
cosmos sdk, but we can take the signer value directly without using that
map.

## Patch
### relayer/provider/cosmos/log.go
```diff
@@ -6,6 +6,7 @@ import (
 	"github.com/cosmos/cosmos-sdk/codec/types"
 	sdk "github.com/cosmos/cosmos-sdk/types"
 	typestx "github.com/cosmos/cosmos-sdk/types/tx"
+	transfertypes "github.com/cosmos/ibc-go/v3/modules/apps/transfer/types"
 	clienttypes "github.com/cosmos/ibc-go/v3/modules/core/02-client/types"
 	"github.com/cosmos/relayer/v2/relayer/provider"
 	"go.uber.org/zap"
@@ -90,6 +91,12 @@ func getFeePayer(tx *typestx.Tx) string {
 	}
 
 	switch firstMsg := tx.GetMsgs()[0].(type) {
+	case *transfertypes.MsgTransfer:
+		// There is a possible data race around concurrent map access
+		// in the cosmos sdk when it converts the address from bech32.
+		// We don't need the address conversion; just the sender is all that
+		// GetSigners is doing under the hood anyway.
+		return firstMsg.Sender
 	case *clienttypes.MsgUpdateClient:
 		// Without this particular special case, there is a panic in ibc-go
 		// due to the sdk config singleton expecting one bech32 prefix but seeing another.
```
