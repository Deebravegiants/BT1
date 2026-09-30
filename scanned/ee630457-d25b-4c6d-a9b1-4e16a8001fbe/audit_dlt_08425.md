# [?] types: prevent temporary power overflows on validator updates  (#4165)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cometbft/cometbft
Published: 2019-11-20
Source: https://github.com/cometbft/cometbft/commit/fc0d5bca61da4419a27e77d31b636cf857c0b042
Type: security-commit

## Details
types: prevent temporary power overflows on validator updates  (#4165)

Closes #4164

## Patch
### CHANGELOG_PENDING.md
```diff
@@ -3,7 +3,7 @@
 \*\*
 
 Special thanks to external contributors on this release:
-@erikgrinaker, @PSalant726
+@erikgrinaker, @PSalant726, @gchaincl
 
 Friendly reminder, we have a [bug bounty
 program](https://hackerone.com/tendermint).
@@ -72,3 +72,4 @@ program](https://hackerone.com/tendermint).
 - [rpc/lib][\#4051](https://github.com/tendermint/tendermint/pull/4131) Fix RPC client, which was previously resolving https protocol to http (@yenkhoon)
 - [rpc][\#4141](https://github.com/tendermint/tendermint/pull/4141) JSONRPCClient: validate that Response.ID matches Request.ID
 - [rpc][\#4141](https://github.com/tendermint/tendermint/pull/4141) WSClient: check for unsolicited responses
+- [types][\4164](https://github.com/tendermint/tendermint/pull/4164) Prevent temporary power overflows on validator updates
```

### types/validator_set.go
```diff
@@ -399,13 +399,14 @@ func verifyUpdates(
 			// Updated validator, add the difference in power to the total.
 			updatedTotalVotingPower += valUpdate.VotingPower - val.VotingPower
 		}
-		overflow := updatedTotalVotingPower > MaxTotalVotingPower
-		if overflow {
-			err = fmt.Errorf(
-				"failed to add/update validator %v, total voting power would exceed the max allowed %v",
-				valUpdate, MaxTotalVotingPower)
-			return 0, 0, err
-		}
+	}
+
+	overflow := updatedTotalVotingPower > MaxTotalVotingPower
+	if overflow {
+		err = fmt.Errorf(
+			"failed to add/update validator, total voting power would exceed the max allowed %v",
+			MaxTotalVotingPower)
+		return 0, 0, err
 	}
 
 	return updatedTotalVotingPower, numNewValidators, nil
```

### types/validator_set_test.go
```diff
@@ -354,6 +354,21 @@ func TestValidatorSetTotalVotingPowerPanicsOnOverflow(t *testing.T) {
 	assert.Panics(t, shouldPanic)
 }
 
+func TestValidatorSetShouldNotErrorOnTemporalOverflow(t *testing.T) {
+	// Updating the validator set might trigger an Overflow error during the update process
+	valSet := NewValidatorSet([]*Validator{
+		{Address: []byte("b"), VotingPower: MaxTotalVotingPower - 1, ProposerPriority: 0},
+		{Address: []byte("a"), VotingPower: 1, ProposerPriority: 0},
+	})
+
+	err := valSet.UpdateWithChangeSet([]*Validator{
+		{Address: []byte("b"), VotingPower: 1, ProposerPriority: 0},
+		{Address: []byte("a"), VotingPower: MaxTotalVotingPower - 1, ProposerPriority: 0},
+	})
+
+	assert.NoError(t, err)
+}
+
 func TestAvgProposerPriority(t *testing.T) {
 	// Create Validator set without calling IncrementProposerPriority:
 	tcs := []struct {
```
