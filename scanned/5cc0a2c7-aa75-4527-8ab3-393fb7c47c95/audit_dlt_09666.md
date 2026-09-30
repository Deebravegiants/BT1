# [?] fix(rollapp): prevent overflow on rollapp state update (#960)

## Summary
Severity: Unknown
Chain: Dymension
Component: dymensionxyz/dymension
Published: 2024-06-24
Source: https://github.com/dymensionxyz/dymension/commit/36430d210fbbd5ee8f33b090d3e66e5892d30145
Type: security-commit

## Details
fix(rollapp): prevent overflow on rollapp state update (#960)

## Patch
### CHANGELOG.md
```diff
@@ -87,6 +87,7 @@ Ref: https://keepachangelog.com/en/1.0.0/
 
 ### Bug Fixes
 
+- (rollapp) [#317](https://github.com/dymensionxyz/research/issues/317) Prevent overflow on rollapp state update
 - (code standards) [#932](https://github.com/dymensionxyz/dymension/issues/932) Dry out existing middlewares to make use of new .GetValidTransfer* functions which take care of parsing and validating the fungible packet, and querying and validating any associated rollapp and finalizations
 - (code standards) [#932](https://github.com/dymensionxyz/dymension/issues/932) Removes the obsolete ValidateRollappId func and sub routines
 - (code standards) [#932](https://github.com/dymensionxyz/dymension/issues/932) Simplify GetAllBlockHeightToFinalizationQueue
```

### x/rollapp/keeper/msg_server_update_state.go
```diff
@@ -7,6 +7,7 @@ import (
 	errorsmod "cosmossdk.io/errors"
 
 	sdk "github.com/cosmos/cosmos-sdk/types"
+
 	"github.com/dymensionxyz/dymension/v3/x/rollapp/types"
 )
 
```

### x/rollapp/types/message_update_state.go
```diff
@@ -1,6 +1,8 @@
 package types
 
 import (
+	"math"
+
 	errorsmod "cosmossdk.io/errors"
 	sdk "github.com/cosmos/cosmos-sdk/types"
 )
@@ -48,11 +50,15 @@ func (msg *MsgUpdateState) ValidateBasic() error {
 		return errorsmod.Wrapf(ErrInvalidAddress, "invalid creator address (%s)", err)
 	}
 
-	// an update cann't be with no BDs
+	// an update can't be with no BDs
 	if msg.NumBlocks == uint64(0) {
 		return errorsmod.Wrap(ErrInvalidNumBlocks, "number of blocks can not be zero")
 	}
 
+	if msg.NumBlocks > math.MaxUint64-msg.StartHeight {
+		return errorsmod.Wrapf(ErrInvalidNumBlocks, "numBlocks(%d) + startHeight(%d) exceeds max uint64", msg.NumBlocks, msg.StartHeight)
+	}
+
 	// check to see that update contains all BDs
 	if len(msg.BDs.BD) != int(msg.NumBlocks) {
 		return errorsmod.Wrapf(ErrInvalidNumBlocks, "number of blocks (%d) != number of block descriptors(%d)", msg.NumBlocks, len(msg.BDs.BD))
```

### x/rollapp/types/message_update_state_test.go
```diff
@@ -3,8 +3,9 @@ package types
 import (
 	"testing"
 
-	"github.com/dymensionxyz/dymension/v3/testutil/sample"
 	"github.com/stretchr/testify/require"
+
+	"github.com/dymensionxyz/dymension/v3/testutil/sample"
 )
 
 var hash32 = []byte("12345678901234567890123456789012")
@@ -124,6 +125,14 @@ func TestMsgUpdateState_ValidateBasic(t *testing.T) {
 				}},
 			},
 			err: ErrInvalidBlockSequence,
+		}, {
+			name: "num blocks overflow",
+			msg: MsgUpdateState{
+				Creator:     sample.AccAddress(),
+				StartHeight: 1,
+				NumBlocks:   ^uint64(0),
+			},
+			err: ErrInvalidNumBlocks,
 		}, {
 			name: "initial state error",
 			msg: MsgUpdateState{
```
