# [?] Merge pull request #1600 from hyunsooda/fix-nil-proposer-panic

## Summary
Severity: Unknown
Chain: Kaia
Component: kaiachain/kaia
Published: 2022-11-15
Source: https://github.com/kaiachain/kaia/commit/690fdeb5177d841b2524c0a8ef6e28d1d45c0f6d
Type: security-commit

## Details
Merge pull request #1600 from hyunsooda/fix-nil-proposer-panic

[CN] Panic by nil access and nil store

## Patch
### consensus/istanbul/validator/default.go
```diff
@@ -279,7 +279,7 @@ func (valSet *defaultSet) CalcProposer(lastProposer common.Address, round uint64
 	defer valSet.validatorMu.RUnlock()
 
 	if len(valSet.validators) == 0 {
-		logger.Error("len of validators is 0, Proposer is nil", "validators", valSet.validators)
+		logger.Error("List of validators is empty", "validators", len(valSet.validators))
 		return
 	}
 
@@ -358,8 +358,12 @@ func (valSet *defaultSet) Copy() istanbul.ValidatorSet {
 	}
 
 	newValSet := NewSubSet(addresses, valSet.policy, valSet.subSize).(*defaultSet)
-	_, proposer := newValSet.GetByAddress(valSet.GetProposer().Address())
-	newValSet.proposer.Store(proposer)
+	if proposer := valSet.GetProposer(); proposer != nil {
+		// Copy the proposer if exist
+		if idx, p := newValSet.GetByAddress(proposer.Address()); idx != -1 {
+			newValSet.proposer.Store(p)
+		}
+	}
 	return newValSet
 }
 
```
