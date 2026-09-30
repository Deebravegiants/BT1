# [?] fix: no-op rather than panic in solomachine update state (#6313)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cosmos/ibc-go
Published: 2024-05-19
Source: https://github.com/cosmos/ibc-go/commit/ca240f80f5666f64f08e9bffe5f7b3347cf25010
Type: security-commit

## Details
fix: no-op rather than panic in solomachine update state (#6313)

* fix: no-op rather than panic in solomachine update state

* Update modules/light-clients/06-solomachine/update.go

Co-authored-by: coderabbitai[bot] <136622811+coderabbitai[bot]@users.noreply.github.com>

* add changelog

---------

Co-authored-by: coderabbitai[bot] <136622811+coderabbitai[bot]@users.noreply.github.com>
Co-authored-by: Carlos Rodriguez <carlos@interchain.io>

## Patch
### CHANGELOG.md
```diff
@@ -57,6 +57,7 @@ Ref: https://keepachangelog.com/en/1.0.0/
 ### State Machine Breaking
 
 * (light-clients/07-tendermint) [\#6276](https://github.com/cosmos/ibc-go/pull/6276) Fix: No-op to avoid panicking on `UpdateState` for invalid misbehaviour submissions.
+* (light-clients/06-solomachine) [\#6313](https://github.com/cosmos/ibc-go/pull/6313) Fix: No-op to avoid panicking on `UpdateState` for invalid misbehaviour submissions.
 
 ### Improvements
 
```

### modules/light-clients/06-solomachine/light_client_module_test.go
```diff
@@ -1042,13 +1042,13 @@ func (suite *SoloMachineTestSuite) TestUpdateState() {
 				nil,
 			},
 			{
-				"failure: invalid type misbehaviour",
+				"invalid type misbehaviour no-ops",
 				func() {
 					clientState = sm.ClientState()
 					clientMsg = sm.CreateMisbehaviour()
 					suite.chainA.App.GetIBCKeeper().ClientKeeper.SetClientState(suite.chainA.GetContext(), clientID, clientState)
 				},
-				fmt.Errorf("unsupported ClientMessage: %T", sm.CreateMisbehaviour()),
+				nil,
 			},
 			{
 				"failure: cannot find client state",
@@ -1092,6 +1092,11 @@ func (suite *SoloMachineTestSuite) TestUpdateState() {
 
 					newClientState := clienttypes.MustUnmarshalClientState(suite.chainA.Codec, clientStateBz)
 
+					if len(consensusHeights) == 0 {
+						suite.Require().Equal(clientState, newClientState)
+						return
+					}
+
 					suite.Require().Len(consensusHeights, 1)
 					suite.Require().Equal(uint64(0), consensusHeights[0].GetRevisionNumber())
 					suite.Require().Equal(newClientState.(*solomachine.ClientState).Sequence, consensusHeights[0].GetRevisionHeight())
```

### modules/light-clients/06-solomachine/update.go
```diff
@@ -1,8 +1,6 @@
 package solomachine
 
 import (
-	"fmt"
-
 	errorsmod "cosmossdk.io/errors"
 	storetypes "cosmossdk.io/store/types"
 
@@ -79,10 +77,12 @@ func (cs ClientState) verifyHeader(cdc codec.BinaryCodec, header *Header) error
 
 // UpdateState updates the consensus state to the new public key and an incremented sequence.
 // A list containing the updated consensus height is returned.
+// If the provided clientMsg is not of type Header, the handler will no-op and return an empty slice.
 func (cs ClientState) UpdateState(ctx sdk.Context, cdc codec.BinaryCodec, clientStore storetypes.KVStore, clientMsg exported.ClientMessage) []exported.Height {
 	smHeader, ok := clientMsg.(*Header)
 	if !ok {
-		panic(fmt.Errorf("unsupported ClientMessage: %T", clientMsg))
+		// clientMsg is invalid Misbehaviour, no update necessary
+		return []exported.Height{}
 	}
 
 	// create new solomachine ConsensusState
```
