# [?] types: prevent spurious validator power overflow warnings when changing the validator set (#4183)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cometbft/cometbft
Published: 2019-11-26
Source: https://github.com/cometbft/cometbft/commit/759ccebe54fb008e2e4947250e389aa55b013893
Type: security-commit

## Details
types: prevent spurious validator power overflow warnings when changing the validator set (#4183)

Fix for #4164
The general problem is that in certain conditions an overflow warning is issued when attempting to update a validator set even if the final set's total voting power is not over the maximum allowed.
Root cause is that in verifyUpdates(), updates are verified wrt to total voting power in the order of validator address. It is then possible that a low address validator may increase its power such that the temporary total voting power count goes over MaxTotalVotingPower.

Scenarios where removing and adding/ updating validators with high voting power, in the same update operation, cause the same false warning and the updates are not applied.

Main changes to fix this are in verifyUpdate() that now does the verification starting with the decreases in power. It also takes into account the removals that are part of the update.

## Commits:

* tests for overflow detection and prevention

* test fix

* more tests

* fix the false overflow warnings and golint

* scopelint warning fix

* review comments

* variant with using sort by amount of change in power

* compute separately number new validators in update

* types: use a switch in processChanges

* more review comments

* types: use HasAddress in numNewValidators

* types: refactor verifyUpdates

copy updates, sort them by delta and use resulting slice to calculate
tvpAfterUpdatesBeforeRemovals.

* remove unused structs

* review comments

* update changelog

### CHANGELOG_PENDING.md
```diff
@@ -100,4 +100,6 @@ program](https://hackerone.com/tendermint).
 - [rpc] [\#4141](https://github.com/tendermint/tendermint/pull/4141) WSClient: check for unsolicited responses
 - [types] [\4164](https://github.com/tendermint/tendermint/pull/4164) Prevent temporary power overflows on validator updates
 - [cs] \#4069 Don't panic when block meta is not found in store (@gregzaitsev)
+- [types] \#4164 Prevent temporary power overflows on validator updates (joint
+  efforts of @gchaincl and @ancazamfir)
 - [p2p] \#4140 `SecretConnection`: use the transcript solely for authentication (i.e. MAC)
```

### types/validator_set.go
```diff
@@ -23,6 +23,7 @@ const (
 	// It could be higher, but this is sufficiently large for our purposes,
 	// and leaves room for defensive purposes.
 	MaxTotalVotingPower = int64(math.MaxInt64) / 8
+
 	// PriorityWindowSizeFactor - is a constant that when multiplied with the total voting power gives
 	// the maximum allowed distance between validator priorities.
 	PriorityWindowSizeFactor = 2
@@ -71,8 +72,8 @@ func (vals *ValidatorSet) IsNilOrEmpty() bool {
 	return vals == nil || len(vals.Validators) == 0
 }
 
-// CopyIncrementProposerPriority increments ProposerPriority and update the
-// proposer on a copy, and return it.
+// CopyIncrementProposerPriority increments ProposerPriority and updates the
+// proposer on a copy, and returns it.
 func (vals *ValidatorSet) CopyIncrementProposerPriority(times int) *ValidatorSet {
 	copy := vals.Copy()
 	copy.IncrementProposerPriority(times)
@@ -106,7 +107,8 @@ func (vals *ValidatorSet) IncrementProposerPriority(times int) {
 	vals.Proposer = proposer
 }
 
-// RescalePriorities ...
+// RescalePriorities rescales the priorities such that the distance between the maximum and minimum
+// is smaller than `diffMax`.
 func (vals *ValidatorSet) RescalePriorities(diffMax int64) {
 	if vals.IsNilOrEmpty() {
 		panic("empty validator set")
@@ -258,7 +260,8 @@ func (vals *ValidatorSet) Size() int {
 	return len(vals.Validators)
 }
 
-// Force recalculation of the set's total voting power.
+// Forces recalculation of the set's total voting power.
+// Panics if total voting power is bigger than MaxTotalVotingPower.
 func (vals *ValidatorSet) updateTotalVotingPower() {
 
 	sum := int64(0)
@@ -330,7 +333,8 @@ func (vals *ValidatorSet) Iterate(fn func(index int, val *Validator) bool) {
 	}
 }
 
-// Checks changes against duplicates, splits the changes in updates and removals, sorts them by address.
+// Checks changes against duplicates, splits the changes in updates and
+// removals, sorts them by address.
 //
 // Returns:
 // updates, removals - the sorted lists of updates and removals
@@ -352,71 +356,93 @@ func processChanges(origChanges []*Validator) (updates, removals []*Validator, e
 			err = fmt.Errorf("duplicate entry %v in %v", valUpdate, changes)
 			return nil, nil, err
 		}
-		if valUpdate.VotingPower < 0 {
-			err = fmt.Errorf("voting power can't be negative: %v", valUpdate)
+
+		switch {
+		case valUpdate.VotingPower < 0:
+			err = fmt.Errorf("voting power can't be negative: %d", valUpdate.VotingPower)
 			return nil, nil, err
-		}
-		if valUpdate.VotingPower > MaxTotalVotingPower {
-			err = fmt.Errorf("to prevent clipping/ overflow, voting power can't be higher than %v: %v ",
-				MaxTotalVotingPower, valUpdate)
+		case valUpdate.VotingPower > MaxTotalVotingPower:
+			err = fmt.Errorf("to prevent clipping/overflow, voting power can't be higher than %d, got %d",
+				MaxTotalVotingPower, valUpdate.VotingPower)
 			return nil, nil, err
-		}
-		if valUpdate.VotingPower == 0 {
+		case valUpdate.VotingPower == 0:
 			removals = append(removals, valUpdate)
-		} else {
+		default:
 			updates = append(updates, valUpdate)
 		}
+
 		prevAddr = valUpdate.Address
 	}
+
 	return updates, removals, err
 }
 
-// Verifies a list of updates against a validator set, making sure the allowed
+// verifyUpdates verifies a list of updates against a validator set, making sure the allowed
 // total voting power would not be exceeded if these updates would be applied to the set.
 //
+// Inputs:
+// updates - a list of proper validator changes, i.e. they have been verified by processChanges for duplicates
+//   and invalid values.
+// vals - the original validator set. Note that vals is NOT modified by this function.
+// removedPower - the total voting power that will be removed after the updates are verified and applied.
+//
 // Returns:
-// updatedTotalVotingPower - the new total voting power if these updates would be applied
-// numNewValidators - number of new validators
-// err - non-nil if the maximum allowed total voting power would be exceeded
+// tvpAfterUpdatesBeforeRemovals -  the new total voting power if these updates would be applied without the removals.
+//   Note that this will be < 2 * MaxTotalVotingPower in case high power validators are removed and
+//   validators are added/ updated with high power values.
 //
-// 'updates' should be a list of proper validator changes, i.e. they have been verified
-// by processChanges for duplicates and invalid values.
-// No changes are made to the validator set 'vals'.
+// err - non-nil if the maximum allowed total voting power would be exceeded
 func verifyUpdates(
 	updates []*Validator,
 	vals *ValidatorSet,
-) (updatedTotalVotingPower int64, numNewValidators int, err error) {
+	removedPower int64,
+) (tvpAfterUpdatesBeforeRemovals int64, err error) {
+	delta := func(update *Validator, vals *ValidatorSet) int64 {
+		_, val := vals.GetByAddress(update.Address)
+		if val != nil {
+			return update.VotingPower - val.VotingPower
+		}
+		return update.VotingPower
+	}
 
-	updatedTotalVotingPower = vals.TotalVotingPower()
+	updatesCopy := validatorListCopy(updates)
+	sort.Slice(updatesCopy, func(i, j int) bool {
+		return delta(updatesCopy[i], vals) < delta(updatesCopy[j], vals)
+	})
 
-	for _, valUpdate := range updates {
-		address := valUpdate.Address
-		_, val := vals.GetByAddress(address)
-		if val == nil {
-			// New validator, add its voting power the the total.
-			updatedTotalVotingPower += valUpdate.VotingPower
-			numNewValidators++
-		} else {
-			// Updated validator, add the difference in power to the total.
-			updatedTotalVotingPower += valUpdate.VotingPower - val.VotingPower
+	tvpAfterRemovals := vals.TotalVotingPower() - removedPower
+	for _, upd := range updatesCopy {
+		tvpAfterRemovals += delta(upd, vals)
+		if tvpAfterRemovals > MaxTotalVotingPower {
+			err = fmt.Errorf(
+				"failed to add/update validator %v, total voting power would exceed the max allowed %v",
+				upd.Address, MaxTotalVotingPower)
+			return 0, err
 		}
 	}
+	return tvpAfterRemovals + removedPower, nil
+}
 
-	overflow := updatedTotalVotingPower > MaxTotalVotingPower
-	if overflow {
-		err = fmt.Errorf(
-			"failed to add/update validator, total voting power would exceed the max allowed %v",
-			MaxTotalVotingPower)
-		return 0, 0, err
+func numNewValidators(updates []*Validator, vals *ValidatorSet) int {
+	numNewValidators := 0
+	for _, valUpdate := range updates {
+		if !vals.HasAddress(valUpdate.Address) {
+			numNewValidators++
+		}
 	}
-
-	return updatedTotalVotingPower, numNewValidators, nil
+	return numNewValidators
 }
 
-// Computes the proposer priority for the validators not present in the set based on 'updatedTotalVotingPower'.
+// computeNewPriorities computes the proposer priority for the validators not present in the set based on
+// 'updatedTotalVotingPower'.
 // Leaves unchanged the priorities of validators that are changed.
 //
 // 'updates' parameter must be a list of unique validators to be added or updated.
+//
+// 'updatedTotalVotingPower' is the total voting power of a set where all updates would be applied but
+//   not the removals. It must be < 2*MaxTotalVotingPower and may be close to this limit if close to
+//   MaxTotalVotingPower will be removed. This is still safe from overflow since MaxTotalVotingPower is maxInt64/8.
+//
 // No changes are made to the validator set 'vals'.
 func computeNewPriorities(updates []*Validator, vals *ValidatorSet, updatedTotalVotingPower int64) {
 
@@ -428,7 +454,7 @@ func computeNewPriorities(updates []*Validator, vals *ValidatorSet, updatedTotal
 			// Set ProposerPriority to -C*totalVotingPower (with C ~= 1.125) to make sure validators can't
 			// un-bond and then re-bond to reset their (potentially previously negative) ProposerPriority to zero.
 			//
-			// Contract: updatedVotingPower < MaxTotalVotingPower to ensure ProposerPriority does
+			// Contract: updatedVotingPower < 2 * MaxTotalVotingPower to ensure ProposerPriority does
 			// not exceed the bounds of int64.
 			//
 			// Compute ProposerPriority = -1.125*totalVotingPower == -(updatedVotingPower + (updatedVotingPower >> 3)).
@@ -482,19 +508,21 @@ func (vals *ValidatorSet) applyUpdates(updates []*Validator) {
 
 // Checks that the validators to be removed are part of the validator set.
 // No changes are made to the validator set 'vals'.
-func verifyRemovals(deletes []*Validator, vals *ValidatorSet) error {
+func verifyRemovals(deletes []*Validator, vals *ValidatorSet) (votingPower int64, err error) {
 
+	removedVotingPower := int64(0)
 	for _, valUpdate := range deletes {
 		address := valUpdate.Address
 		_, val := vals.GetByAddress(address)
 		if val == nil {
-			return fmt.Errorf("failed to find validator %X to remove", address)
+			return removedVotingPower, fmt.Errorf("failed to find validator %X to remove", address)
 		}
+		removedVotingPower += val.VotingPower
 	}
 	if len(deletes) > len(vals.Validators) {
 		panic("more deletes than validators")
 	}
-	return nil
+	return removedVotingPower, nil
 }
 
 // Removes the validators specified in 'deletes' from validator set 'vals'.
@@ -546,30 +574,33 @@ func (vals *ValidatorSet) updateWithChangeSet(changes []*Validator, allowDeletes
 		return fmt.Errorf("cannot process validators with voting power 0: %v", deletes)
 	}
 
+	// Check that the resulting set will not be empty.
+	if numNewValidators(updates, vals) == 0 && len(vals.Validators) == len(deletes) {
+		return errors.New("applying the validator changes would result in empty set")
+	}
+
 	// Verify that applying the 'deletes' against 'vals' will not result in error.
-	if err := verifyRemovals(deletes, vals); err != nil {
+	// Get the voting power that is going to be removed.
+	removedVotingPower, err := verifyRemovals(deletes, vals)
+	if err != nil {
 		return err
 	}
 
 	// Verify that applying the 'updates' against 'vals' will not result in error.
-	updatedTotalVotingPower, numNewValidators, err := verifyUpdates(updates, vals)
+	// Get the updated total voting power before removal. Note that this is < 2 * MaxTotalVotingPower
+	tvpAfterUpdatesBeforeRemovals, err := verifyUpdates(updates, vals, removedVotingPower)
 	if err != nil {
 		return err
 	}
 
-	// Check that the resulting set will not be empty.
-	if numNewValidators == 0 && len(vals.Validators) == len(deletes) {
-		return errors.New("applying the validator changes would result in empty set")
-	}
-
 	// Compute the priorities for updates.
-	computeNewPriorities(updates, vals, updatedTotalVotingPower)
+	computeNewPriorities(updates, vals, tvpAfterUpdatesBeforeRemovals)
 
 	// Apply updates and removals.
 	vals.applyUpdates(updates)
 	vals.applyRemovals(deletes)
 
-	vals.updateTotalVotingPower()
+	vals.updateTotalVotingPower() // will panic if total voting power > MaxTotalVotingPower
 
 	// Scale and center.
 	vals.RescalePriorities(PriorityWindowSizeFactor * vals.TotalVotingPower())
@@ -830,7 +861,7 @@ func (vals *ValidatorSet) StringIndented(indent string) string {
 //-------------------------------------
 // Implements sort for sorting validators by address.
 
-// ValidatorsByAddress is used to sort validators by address.
+// ValidatorsByAddress implements the sort of validators by address.
 type ValidatorsByAddress []*Validator
 
 func (valz ValidatorsByAddress) Len() int {
```

### types/validator_set_test.go
```diff
@@ -46,7 +46,7 @@ func TestValidatorSetBasic(t *testing.T) {
 	assert.Nil(t, vset.Hash())
 
 	// add
-	val = randValidator_(vset.TotalVotingPower())
+	val = randValidator(vset.TotalVotingPower())
 	assert.NoError(t, vset.UpdateWithChangeSet([]*Validator{val}))
 
 	assert.True(t, vset.HasAddress(val.Address))
@@ -61,7 +61,7 @@ func TestValidatorSetBasic(t *testing.T) {
 	assert.Equal(t, val.Address, vset.GetProposer().Address)
 
 	// update
-	val = randValidator_(vset.TotalVotingPower())
+	val = randValidator(vset.TotalVotingPower())
 	assert.NoError(t, vset.UpdateWithChangeSet([]*Validator{val}))
 	_, val = vset.GetByAddress(val.Address)
 	val.VotingPower += 100
@@ -304,7 +304,7 @@ func randPubKey() crypto.PubKey {
 	return ed25519.PubKeyEd25519(pubKey)
 }
 
-func randValidator_(totalVotingPower int64) *Validator {
+func randValidator(totalVotingPower int64) *Validator {
 	// this modulo limits the ProposerPriority/VotingPower to stay in the
 	// bounds of MaxTotalVotingPower minus the already existing voting power:
 	val := NewValidator(randPubKey(), int64(cmn.RandUint64()%uint64((MaxTotalVotingPower-totalVotingPower))))
@@ -316,7 +316,7 @@ func randValidatorSet(numValidators int) *ValidatorSet {
 	validators := make([]*Validator, numValidators)
 	totalVotingPower := int64(0)
 	for i := 0; i < numValidators; i++ {
-		validators[i] = randValidator_(totalVotingPower)
+		validators[i] = randValidator(totalVotingPower)
 		totalVotingPower += validators[i].VotingPower
 	}
 	return NewValidatorSet(validators)
@@ -354,21 +354,6 @@ func TestValidatorSetTotalVotingPowerPanicsOnOverflow(t *testing.T) {
 	assert.Panics(t, shouldPanic)
 }
 
-func TestValidatorSetShouldNotErrorOnTemporalOverflow(t *testing.T) {
-	// Updating the validator set might trigger an Overflow error during the update process
-	valSet := NewValidatorSet([]*Validator{
-		{Address: []byte("b"), VotingPower: MaxTotalVotingPower - 1, ProposerPriority: 0},
-		{Address: []byte("a"), VotingPower: 1, ProposerPriority: 0},
-	})
-
-	err := valSet.UpdateWithChangeSet([]*Validator{
-		{Address: []byte("b"), VotingPower: 1, ProposerPriority: 0},
-		{Address: []byte("a"), VotingPower: MaxTotalVotingPower - 1, ProposerPriority: 0},
-	})
-
-	assert.NoError(t, err)
-}
-
 func TestAvgProposerPriority(t *testing.T) {
 	// Create Validator set without calling IncrementProposerPriority:
 	tcs := []struct {
@@ -1108,11 +1093,13 @@ func TestValSetApplyUpdatesTestsExecute(t *testing.T) {
 }
 
 type testVSetCfg struct {
+	name         string
 	startVals    []testVal
 	deletedVals  []testVal
 	updatedVals  []testVal
 	addedVals    []testVal
 	expectedVals []testVal
+	wantErr      bool
 }
 
 func randTestVSetCfg(t *testing.T, nBase, nAddMax int) testVSetCfg {
@@ -1170,14 +1157,14 @@ func randTestVSetCfg(t *testing.T, nBase, nAddMax int) testVSetCfg {
 
 }
 
-func applyChangesToValSet(t *testing.T, valSet *ValidatorSet, valsLists ...[]testVal) {
+func applyChangesToValSet(t *testing.T, wantErr bool, valSet *ValidatorSet, valsLists ...[]testVal) {
 	changes := make([]testVal, 0)
 	for _, valsList := range valsLists {
 		changes = append(changes, valsList...)
 	}
 	valList := createNewValidatorList(changes)
 	err := valSet.UpdateWithChangeSet(valList)
-	assert.NoError(t, err)
+	assert.Equal(t, wantErr, err != nil, "got error %v", err)
 }
 
 func TestValSetUpdatePriorityOrderTests(t *testing.T) {
@@ -1236,19 +1223,18 @@ func TestValSetUpdatePriorityOrderTests(t *testing.T) {
 }
 
 func verifyValSetUpdatePriorityOrder(t *testing.T, valSet *ValidatorSet, cfg testVSetCfg, nMaxElections int) {
-
 	// Run election up to nMaxElections times, sort validators by priorities
 	valSet.IncrementProposerPriority(cmn.RandInt()%nMaxElections + 1)
 	origValsPriSorted := validatorListCopy(valSet.Validators)
 	sort.Sort(validatorsByPriority(origValsPriSorted))
 
 	// apply the changes, get the updated validators, sort by priorities
-	applyChangesToValSet(t, valSet, cfg.addedVals, cfg.updatedVals, cfg.deletedVals)
+	applyChangesToValSet(t, false, valSet, cfg.addedVals, cfg.updatedVals, cfg.deletedVals)
 	updatedValsPriSorted := validatorListCopy(valSet.Validators)
 	sort.Sort(validatorsByPriority(updatedValsPriSorted))
 
 	// basic checks
-	assert.Equal(t, toTestValList(valSet.Validators), cfg.expectedVals)
+	assert.Equal(t, cfg.expectedVals, toTestValList(valSet.Validators))
 	verifyValidatorSet(t, valSet)
 
 	// verify that the added validators have the smallest priority:
@@ -1266,6 +1252,77 @@ func verifyValSetUpdatePriorityOrder(t *testing.T, valSet *ValidatorSet, cfg tes
 	}
 }
 
+func TestValSetUpdateOverflowRelated(t *testing.T) {
+	testCases := []testVSetCfg{
+		{
+			name:         "1 no false overflow error messages for updates",
+			startVals:    []testVal{{"v1", 1}, {"v2", MaxTotalVotingPower - 1}},
+			updatedVals:  []testVal{{"v1", MaxTotalVotingPower - 1}, {"v2", 1}},
+			expectedVals: []testVal{{"v1", MaxTotalVotingPower - 1}, {"v2", 1}},
+			wantErr:      false,
+		},
+		{
+			// this test shows that it is important to apply the updates in the order of the change in power
+			// i.e. apply first updates with decreases in power, v2 change in this case.
+			name:         "2 no false overflow error messages for updates",
+			startVals:    []testVal{{"v1", 1}, {"v2", MaxTotalVotingPower - 1}},
+			updatedVals:  []testVal{{"v1", MaxTotalVotingPower/2 - 1}, {"v2", MaxTotalVotingPower / 2}},
+			expectedVals: []testVal{{"v1", MaxTotalVotingPower/2 - 1}, {"v2", MaxTotalVotingPower / 2}},
+			wantErr:      false,
+		},
+		{
+			name:         "3 no false overflow error messages for deletes",
+			startVals:    []testVal{{"v1", MaxTotalVotingPower - 2}, {"v2", 1}, {"v3", 1}},
+			deletedVals:  []testVal{{"v1", 0}},
+			addedVals:    []testVal{{"v4", MaxTotalVotingPower - 2}},
+			expectedVals: []testVal{{"v2", 1}, {"v3", 1}, {"v4", MaxTotalVotingPower - 2}},
+			wantErr:      false,
+		},
+		{
+			name: "4 no false overflow error messages for adds, updates and deletes",
+			startVals: []testVal{
+				{"v1", MaxTotalVotingPower / 4}, {"v2", MaxTotalVotingPower / 4},
+				{"v3", MaxTotalVotingPower / 4}, {"v4", MaxTotalVotingPower / 4}},
+			deletedVals: []testVal{{"v2", 0}},
+			updatedVals: []testVal{
+				{"v1", MaxTotalVotingPower/2 - 2}, {"v3", MaxTotalVotingPower/2 - 3}, {"v4", 2}},
+			addedVals: []testVal{{"v5", 3}},
+			expectedVals: []testVal{
+				{"v1", MaxTotalVotingPower/2 - 2}, {"v3", MaxTotalVotingPower/2 - 3}, {"v4", 2}, {"v5", 3}},
+			wantErr: false,
+		},
+		{
+			name: "5 check panic on overflow is prevented: update 8 validators with power int64(math.MaxInt64)/8",
+			startVals: []testVal{
+				{"v1", 1}, {"v2", 1}, {"v3", 1}, {"v4", 1}, {"v5", 1},
+				{"v6", 1}, {"v7", 1}, {"v8", 1}, {"v9", 1}},
+			updatedVals: []testVal{
+				{"v1", MaxTotalVotingPower}, {"v2", MaxTotalVotingPower}, {"v3", MaxTotalVotingPower},
+				{"v4", MaxTotalVotingPower}, {"v5", MaxTotalVotingPower}, {"v6", MaxTotalVotingPower},
+				{"v7", MaxTotalVotingPower}, {"v8", MaxTotalVotingPower}, {"v9", 8}},
+			expectedVals: []testVal{
+				{"v1", 1}, {"v2", 1}, {"v3", 1}, {"v4", 1}, {"v5", 1},
+				{"v6", 1}, {"v7", 1}, {"v8", 1}, {"v9", 1}},
+			wantErr: true,
+		},
+	}
+
+	for _, tt := range testCases {
+		tt := tt
+		t.Run(tt.name, func(t *testing.T) {
+			valSet := createNewValidatorSet(tt.startVals)
+			verifyValidatorSet(t, valSet)
+
+			// execute update and verify returned error is as expected
+			applyChangesToValSet(t, tt.wantErr, valSet, tt.addedVals, tt.updatedVals, tt.deletedVals)
+
+			// verify updated validator set is as expected
+			assert.Equal(t, tt.expectedVals, toTestValList(valSet.Validators))
+			verifyValidatorSet(t, valSet)
+		})
+	}
+}
+
 //---------------------
 // Sort validators by priority and address
 type validatorsByPriority []*Validator
```
