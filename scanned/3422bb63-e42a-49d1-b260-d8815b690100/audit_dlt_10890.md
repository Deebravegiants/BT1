# [?] fix: distribute rewards is panicing in e2e! (#96)

## Summary
Severity: Unknown
Chain: VeChain
Component: vechain/thor
Published: 2025-05-01
Source: https://github.com/vechain/thor/commit/9602a4a50d91f1e987a017eaf63a1b8feeae75df
Type: security-commit

## Details
fix: distribute rewards is panicing in e2e! (#96)

## Patch
### builtin/energy/energy.go
```diff
@@ -202,23 +202,22 @@ func (e *Energy) addIssued(issued *big.Int) error {
 
 type staker interface {
 	LockedVET() (*big.Int, error)
-	GetDelegationLockedVET(validationID thor.Bytes32) (*big.Int, error)
+	HasDelegations(address thor.Address) (bool, error)
 }
 
-func (e *Energy) DistributeRewards(validationID thor.Bytes32, beneficiary thor.Address, staker staker) error {
+func (e *Energy) DistributeRewards(beneficiary, signer thor.Address, staker staker) error {
 	reward, err := e.CalculateRewards(staker)
 	if err != nil {
 		return err
 	}
-
-	delegatedVET, err := staker.GetDelegationLockedVET(validationID)
+	hasDelegations, err := staker.HasDelegations(signer)
 	if err != nil {
 		return err
 	}
 
 	// If delegated amount of VET is 0 then transfer the whole reward to the validator
 	proposerReward := new(big.Int).Set(reward)
-	if delegatedVET.Cmp(big.NewInt(0)) != 0 {
+	if hasDelegations {
 		proposerReward.Mul(proposerReward, big.NewInt(3))
 		proposerReward.Div(proposerReward, big.NewInt(10))
 
```

### builtin/staker/staker.go
```diff
@@ -194,15 +194,26 @@ func (s *Staker) GetDelegator(
 	return s.storage.GetDelegator(delegationID)
 }
 
-// GetDelegation returns the delegation.
-func (s *Staker) GetDelegationLockedVET(
-	validationID thor.Bytes32,
-) (*big.Int, error) {
+// HasDelegations returns true if the validator has any delegations.
+func (s *Staker) HasDelegations(
+	master thor.Address,
+) (bool, error) {
+	_, validationID, err := s.storage.LookupMaster(master)
+	if err != nil {
+		return false, err
+	}
+	if validationID.IsZero() {
+		return false, nil
+	}
 	delegation, err := s.storage.GetDelegation(validationID)
 	if err != nil {
-		return nil, err
+		return false, err
+	}
+	if delegation == nil || delegation.IsEmpty() {
+		return false, nil
 	}
-	return delegation.LockedVET, nil
+	total := new(big.Int).Add(delegation.LockedVET, delegation.CooldownVET)
+	return total.Sign() > 0, nil
 }
 
 // UpdateDelegatorAutoRenew updates the auto-renewal status of a delegator.
```

### consensus/validator.go
```diff
@@ -269,13 +269,9 @@ func (c *Consensus) verifyBlock(blk *block.Block, state *state.State, blockConfl
 
 	if posActive {
 		// TODO: We can reward priority fees here too
-		stakerContract := builtin.Staker.Native(state)
+		staker := builtin.Staker.Native(state)
 		energy := builtin.Energy.Native(state, header.Timestamp())
-		_, validationID, err := stakerContract.LookupMaster(signer)
-		if err != nil {
-			return nil, nil, err
-		}
-		if err := energy.DistributeRewards(validationID, blk.Header().Beneficiary(), stakerContract); err != nil {
+		if err := energy.DistributeRewards(blk.Header().Beneficiary(), signer, staker); err != nil {
 			return nil, nil, err
 		}
 	}
```

### packer/flow.go
```diff
@@ -163,13 +163,10 @@ func (f *Flow) Pack(privateKey *ecdsa.PrivateKey, newBlockConflicts uint32, shou
 
 	if f.posActive {
 		// TODO: We can reward priority fees here too
-		stakerContract := builtin.Staker.Native(f.runtime.State())
+		signer := crypto.PubkeyToAddress(privateKey.PublicKey)
+		staker := builtin.Staker.Native(f.runtime.State())
 		energy := builtin.Energy.Native(f.runtime.State(), f.runtime.Context().Time)
-		_, validationID, err := stakerContract.LookupMaster(f.packer.nodeMaster)
-		if err != nil {
-			return nil, nil, nil, err
-		}
-		if err := energy.DistributeRewards(validationID, f.runtime.Context().Beneficiary, stakerContract); err != nil {
+		if err := energy.DistributeRewards(f.runtime.Context().Beneficiary, thor.Address(signer), staker); err != nil {
 			return nil, nil, nil, err
 		}
 	}
```
