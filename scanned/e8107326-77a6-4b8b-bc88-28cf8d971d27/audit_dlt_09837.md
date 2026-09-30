# [?] add crash protection for staking msg type cast

## Summary
Severity: Unknown
Chain: Harmony
Component: harmony-one/harmony
Published: 2019-10-24
Source: https://github.com/harmony-one/harmony/commit/6ceede98f53621058214705567ade4fcd973979b
Type: security-commit

## Details
add crash protection for staking msg type cast

## Patch
### staking/types/transaction.go
```diff
@@ -12,6 +12,10 @@ import (
 	"github.com/harmony-one/harmony/crypto/hash"
 )
 
+var (
+	errStakingTransactionTypeCastErr = errors.New("Cannot type cast to matching staking type")
+)
+
 type txdata struct {
 	Directive
 	StakeMsg     interface{}
@@ -159,19 +163,34 @@ func (tx *StakingTransaction) StakingMsgToBytes() (by []byte, err error) {
 
 	switch stakeType {
 	case DirectiveCreateValidator:
-		createValidator := tx.StakingMessage().(CreateValidator)
+		createValidator, ok := tx.StakingMessage().(CreateValidator)
+		if !ok {
+			return nil, errStakingTransactionTypeCastErr
+		}
 		by, err = rlp.EncodeToBytes(createValidator)
 	case DirectiveEditValidator:
-		editValidator := tx.StakingMessage().(EditValidator)
+		editValidator, ok := tx.StakingMessage().(EditValidator)
+		if !ok {
+			return nil, errStakingTransactionTypeCastErr
+		}
 		by, err = rlp.EncodeToBytes(editValidator)
 	case DirectiveDelegate:
-		delegate := tx.StakingMessage().(Delegate)
+		delegate, ok := tx.StakingMessage().(Delegate)
+		if !ok {
+			return nil, errStakingTransactionTypeCastErr
+		}
 		by, err = rlp.EncodeToBytes(delegate)
 	case DirectiveUndelegate:
-		undelegate := tx.StakingMessage().(Undelegate)
+		undelegate, ok := tx.StakingMessage().(Undelegate)
+		if !ok {
+			return nil, errStakingTransactionTypeCastErr
+		}
 		by, err = rlp.EncodeToBytes(undelegate)
 	case DirectiveCollectRewards:
-		collectRewards := tx.StakingMessage().(CollectRewards)
+		collectRewards, ok := tx.StakingMessage().(CollectRewards)
+		if !ok {
+			return nil, errStakingTransactionTypeCastErr
+		}
 		by, err = rlp.EncodeToBytes(collectRewards)
 	default:
 		by = []byte{}
```
