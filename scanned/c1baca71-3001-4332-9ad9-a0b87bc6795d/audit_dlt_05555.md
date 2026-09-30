# [?] fix: decrease overflow (#1348)

## Summary
Severity: Unknown
Chain: VeChain
Component: vechain/thor
Published: 2025-09-17
Source: https://github.com/vechain/thor/commit/7bccbf010723035ad707b4d3a4ea93df715aec43
Type: security-commit

## Details
fix: decrease overflow (#1348)

* fix: decrease overflow

* chore: decrease stake amount check

* chore: add unit test

* chore: add unit test

* chore: move increase check to function

---------

Co-authored-by: Miguel Angel Rojo <freemanz1486@gmail.com>

## Patch
### builtin/staker/staker.go
```diff
@@ -211,9 +211,11 @@ func (s *Staker) AddValidation(
 		"period", period,
 		"stake", stake,
 	)
-
-	if stake < MinStakeVET || stake > MaxStakeVET {
-		return NewReverts("stake is out of range")
+	if stake < MinStakeVET {
+		return NewReverts("stake is below minimum")
+	}
+	if stake > MaxStakeVET {
+		return NewReverts("stake is above maximum")
 	}
 
 	if validator.IsZero() {
@@ -330,6 +332,9 @@ func (s *Staker) IncreaseStake(validator thor.Address, endorser thor.Address, am
 
 func (s *Staker) DecreaseStake(validator thor.Address, endorser thor.Address, amount uint64) error {
 	logger.Debug("decreasing stake", "endorser", endorser, "validator", validator, "amount", amount)
+	if amount > MaxStakeVET-MinStakeVET {
+		return NewReverts("decrease amount is too large")
+	}
 
 	val, err := s.getValidationOrRevert(validator)
 	if err != nil {
@@ -346,21 +351,21 @@ func (s *Staker) DecreaseStake(validator thor.Address, endorser thor.Address, am
 		return NewReverts("validator has signaled exit, cannot decrease stake")
 	}
 
+	var nextPeriodVET uint64
 	if val.Status == validation.StatusActive {
 		// We don't consider any increases, i.e., entry.QueuedVET. We only consider locked and current decreases.
 		// The reason is that validator can instantly withdraw QueuedVET at any time.
 		// We need to make sure the locked VET minus the sum of the current decreases is still above the minimum stake.
-		pendingAndDecrease := val.PendingUnlockVET + amount
-		if pendingAndDecrease > val.LockedVET || val.LockedVET-pendingAndDecrease < MinStakeVET {
-			return NewReverts("next period stake is lower than minimum stake")
-		}
+		nextPeriodVET = val.LockedVET - val.PendingUnlockVET
 	}
-
 	if val.Status == validation.StatusQueued {
-		// All the validator's stake exists within QueuedVET, so we need to make sure it maintains a minimum of MinStake.
-		if val.QueuedVET-amount < MinStakeVET {
-			return NewReverts("next period stake is lower than minimum stake")
-		}
+		nextPeriodVET = val.QueuedVET
+	}
+	if amount > nextPeriodVET {
+		return NewReverts("not enough locked stake")
+	}
+	if nextPeriodVET-amount < MinStakeVET {
+		return NewReverts("next period stake is lower than minimum stake")
 	}
 
 	if err = s.validationService.DecreaseStake(validator, val, amount); err != nil {
@@ -636,6 +641,9 @@ func (s *Staker) IncreaseDelegatorsReward(node thor.Address, reward *big.Int, cu
 }
 
 func (s *Staker) validateStakeIncrease(validator thor.Address, validation *validation.Validation, amount uint64) error {
+	if amount > MaxStakeVET {
+		return NewReverts("increase amount is too large")
+	}
 	agg, err := s.aggregationService.GetAggregation(validator)
 	if err != nil {
 		return err
```

### builtin/staker/staker_test.go
```diff
@@ -726,7 +726,7 @@ func TestValidationAdd_Error(t *testing.T) {
 	id1 := thor.BytesToAddress([]byte("id1"))
 
 	assert.ErrorContains(t, staker.AddValidation(id1, id1, uint32(1), MinStakeVET), "period is out of boundaries")
-	assert.ErrorContains(t, staker.AddValidation(id1, id1, thor.LowStakingPeriod(), 0), "stake is out of range")
+	assert.ErrorContains(t, staker.AddValidation(id1, id1, thor.LowStakingPeriod(), 0), "stake is below minimum")
 	assert.NoError(t, staker.AddValidation(id1, id1, thor.LowStakingPeriod(), MinStakeVET))
 	assert.ErrorContains(t, staker.AddValidation(id1, id1, thor.LowStakingPeriod(), MinStakeVET), "validator already exists")
 }
```

### builtin/staker/validations_test.go
```diff
@@ -7,6 +7,7 @@
 package staker
 
 import (
+	"math"
 	"math/big"
 	"math/rand/v2"
 	"testing"
@@ -203,7 +204,7 @@ func TestStaker_AddValidation_MinimumStake(t *testing.T) {
 
 	tooLow := MinStakeVET - 1
 	err := staker.AddValidation(datagen.RandAddress(), datagen.RandAddress(), uint32(360)*24*15, tooLow)
-	assert.ErrorContains(t, err, "stake is out of range")
+	assert.ErrorContains(t, err, "stake is below minimum")
 	err = staker.AddValidation(datagen.RandAddress(), datagen.RandAddress(), uint32(360)*24*15, MinStakeVET)
 	assert.NoError(t, err)
 }
@@ -213,7 +214,7 @@ func TestStaker_AddValidation_MaximumStake(t *testing.T) {
 
 	tooHigh := MaxStakeVET + 1
 	err := staker.AddValidation(datagen.RandAddress(), datagen.RandAddress(), uint32(360)*24*15, tooHigh)
-	assert.ErrorContains(t, err, "stake is out of range")
+	assert.ErrorContains(t, err, "stake is above maximum")
 	err = staker.AddValidation(datagen.RandAddress(), datagen.RandAddress(), uint32(360)*24*15, MaxStakeVET)
 	assert.NoError(t, err)
 }
@@ -3337,3 +3338,29 @@ func TestValidation_NegativeCases(t *testing.T) {
 	_, err = staker.GetValidation(node1)
 	assert.Error(t, err)
 }
+
+func TestValidation_DecreaseOverflow(t *testing.T) {
+	staker, _ := newStaker(t, 0, 1, false)
+	addr := datagen.RandAddress()
+	endorser := datagen.RandAddress()
+
+	newTestSequence(t, staker).AddValidation(addr, endorser, thor.MediumStakingPeriod(), MinStakeVET)
+
+	overflowDecrease := math.MaxUint64 - MinStakeVET - 1
+	assert.ErrorContains(t, staker.DecreaseStake(addr, endorser, overflowDecrease), "decrease amount is too large")
+
+	assertValidation(t, staker, addr).QueuedVET(MinStakeVET)
+}
+
+func TestValidation_IncreaseOverflow(t *testing.T) {
+	staker, _ := newStaker(t, 0, 1, false)
+	addr := datagen.RandAddress()
+	endorser := datagen.RandAddress()
+
+	newTestSequence(t, staker).AddValidation(addr, endorser, thor.MediumStakingPeriod(), MinStakeVET)
+
+	overflowIncrease := math.MaxUint64 - MinStakeVET + 1
+	assert.ErrorContains(t, staker.IncreaseStake(addr, endorser, overflowIncrease), "increase amount is too large")
+
+	assertValidation(t, staker, addr).QueuedVET(MinStakeVET)
+}
```
