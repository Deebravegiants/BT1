# [?] [state] ValidatorWrapper div zero panic fix -  (#2724)

## Summary
Severity: Unknown
Chain: Harmony
Component: harmony-one/harmony
Published: 2020-04-04
Source: https://github.com/harmony-one/harmony/commit/24a17feecdbd91b8bc3c8a758be6e2f0c2e2b973
Type: security-commit

## Details
[state] ValidatorWrapper div zero panic fix -  (#2724)

* [state] Error on div zero

* [state] Do not pay out commit when commit is 0%

* [state] Put whole commission in guarded block

* [core] Reward cannot be zero

* [state] return nil, not hard error

## Patch
### core/state/statedb.go
```diff
@@ -748,8 +748,18 @@ func (db *DB) IsValidator(addr common.Address) bool {
 	return so.IsValidator(db.db)
 }
 
+var (
+	zero = numeric.ZeroDec()
+)
+
 // AddReward distributes the reward to all the delegators based on stake percentage.
 func (db *DB) AddReward(snapshot *stk.ValidatorWrapper, reward *big.Int) error {
+	if reward.Cmp(common.Big0) == 0 {
+		utils.Logger().Info().RawJSON("validator", []byte(snapshot.String())).
+			Msg("0 given as reward")
+		return nil
+	}
+
 	curValidator, err := db.ValidatorWrapper(snapshot.Address)
 	if err != nil {
 		return errors.Wrapf(err, "failed to distribute rewards: validator does not exist")
@@ -765,15 +775,26 @@ func (db *DB) AddReward(snapshot *stk.ValidatorWrapper, reward *big.Int) error {
 	rewardPool := big.NewInt(0).Set(reward)
 	curValidator.BlockReward.Add(curValidator.BlockReward, reward)
 	// Payout commission
-	commissionInt := snapshot.Validator.CommissionRates.Rate.MulInt(reward).RoundInt()
-	curValidator.Delegations[0].Reward.Add(curValidator.Delegations[0].Reward, commissionInt)
-	rewardPool.Sub(rewardPool, commissionInt)
+	if r := snapshot.Validator.CommissionRates.Rate; r.GT(zero) {
+		commissionInt := r.MulInt(reward).RoundInt()
+		curValidator.Delegations[0].Reward.Add(
+			curValidator.Delegations[0].Reward,
+			commissionInt,
+		)
+		rewardPool.Sub(rewardPool, commissionInt)
+	}
 	totalRewardForDelegators := big.NewInt(0).Set(rewardPool)
 	// Payout each delegator's reward pro-rata
 	totalDelegationDec := numeric.NewDecFromBigInt(snapshot.TotalDelegation())
 	for i := range snapshot.Delegations {
 		delegation := snapshot.Delegations[i]
 		// NOTE percentage = <this_delegator_amount>/<total_delegation>
+		if totalDelegationDec.Equal(zero) {
+			utils.Logger().Info().
+				RawJSON("validator-snapshot", []byte(snapshot.String())).
+				Msg("zero total delegation during AddReward delegation payout")
+			return nil
+		}
 		percentage := numeric.NewDecFromBigInt(delegation.Amount).Quo(totalDelegationDec)
 		rewardInt := percentage.MulInt(totalRewardForDelegators).RoundInt()
 		curDelegation := curValidator.Delegations[i]
```
