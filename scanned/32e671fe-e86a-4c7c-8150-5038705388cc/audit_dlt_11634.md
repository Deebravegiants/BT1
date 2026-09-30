# [?] x/interchainstaking/keeper: fix non-determinism in msgServer.RequestRedemption (#143)

## Summary
Severity: Unknown
Chain: Quicksilver
Component: quicksilver-zone/quicksilver
Published: 2022-07-28
Source: https://github.com/quicksilver-zone/quicksilver/commit/951693d56a403263ae92ed705f03d1ad7ebae6db
Type: security-commit

## Details
x/interchainstaking/keeper: fix non-determinism in msgServer.RequestRedemption (#143)

Previously the code that invoked keeper.SubmitTx relied on
the range order from map iteration, which in Go is guaranteed
to be randomized hence non-deterministic. This change fixes that
by firstly grabbing out delegator addresses into a slice, sorting
that slice and then iterating on the sorted slice.

Fixes #142

## Patch
### x/interchainstaking/keeper/msg_server.go
```diff
@@ -6,6 +6,7 @@ import (
 	"encoding/binary"
 	"encoding/hex"
 	"fmt"
+	"sort"
 
 	sdk "github.com/cosmos/cosmos-sdk/types"
 	"github.com/cosmos/cosmos-sdk/types/bech32"
@@ -142,7 +143,13 @@ func (k msgServer) RequestRedemption(goCtx context.Context, msg *types.MsgReques
 		}
 	}
 
-	for delegator, _ := range msgs {
+	delegators := make([]string, 0, len(msgs))
+	for delegator := range msgs {
+		delegators = append(delegators, delegator)
+	}
+	sort.Strings(delegators)
+
+	for _, delegator := range delegators {
 		icaAccount, err := zone.GetDelegationAccountByAddress(delegator)
 		if err != nil {
 			panic(err) // panic here because something is terribly wrong if we cann't find the delegation bucket here!!!
```
