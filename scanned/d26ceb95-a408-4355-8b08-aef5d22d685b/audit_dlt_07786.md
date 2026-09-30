# [?] Fix Multivalue Slice Deadlock (#13087)

## Summary
Severity: Unknown
Chain: Ethereum
Component: OffchainLabs/prysm
Published: 2023-10-21
Source: https://github.com/OffchainLabs/prysm/commit/f91efafe24409e25180d0aeb6488e59c4b9f1b79
Type: security-commit

## Details
Fix Multivalue Slice Deadlock (#13087)

* fix deadlock

* gofmt

* lint

## Patch
### beacon-chain/state/state-native/references_test.go
```diff
@@ -9,6 +9,7 @@ import (
 	"github.com/prysmaticlabs/go-bitfield"
 	"github.com/prysmaticlabs/prysm/v4/beacon-chain/state"
 	"github.com/prysmaticlabs/prysm/v4/beacon-chain/state/state-native/types"
+	"github.com/prysmaticlabs/prysm/v4/config/features"
 	"github.com/prysmaticlabs/prysm/v4/encoding/bytesutil"
 	ethpb "github.com/prysmaticlabs/prysm/v4/proto/prysm/v1alpha1"
 	"github.com/prysmaticlabs/prysm/v4/testing/assert"
@@ -1015,6 +1016,43 @@ func TestValidatorReferences_RemainsConsistent_Bellatrix(t *testing.T) {
 	}))
 }
 
+func TestValidatorReferences_ApplyValidator_BalancesRead(t *testing.T) {
+	resetCfg := features.InitWithReset(&features.Flags{
+		EnableExperimentalState: true,
+	})
+	defer resetCfg()
+	s, err := InitializeFromProtoUnsafeAltair(&ethpb.BeaconStateAltair{
+		Validators: []*ethpb.Validator{
+			{PublicKey: []byte{'A'}},
+			{PublicKey: []byte{'B'}},
+			{PublicKey: []byte{'C'}},
+			{PublicKey: []byte{'D'}},
+			{PublicKey: []byte{'E'}},
+		},
+		Balances: []uint64{0, 0, 0, 0, 0},
+	})
+	require.NoError(t, err)
+	a, ok := s.(*BeaconState)
+	require.Equal(t, true, ok)
+
+	// Create a second state.
+	copied := a.Copy()
+	b, ok := copied.(*BeaconState)
+	require.Equal(t, true, ok)
+
+	// Modify all validators from copied state, it should not deadlock.
+	assert.NoError(t, b.ApplyToEveryValidator(func(idx int, val *ethpb.Validator) (bool, *ethpb.Validator, error) {
+		b, err := b.BalanceAtIndex(0)
+		if err != nil {
+			return false, nil, err
+		}
+		newVal := ethpb.CopyValidator(val)
+		newVal.EffectiveBalance += b
+		val.EffectiveBalance += b
+		return true, val, nil
+	}))
+}
+
 // assertRefCount checks whether reference count for a given state
 // at a given index is equal to expected amount.
 func assertRefCount(t *testing.T, b *BeaconState, idx types.FieldIndex, want uint) {
```

### beacon-chain/state/state-native/setters_validator.go
```diff
@@ -41,30 +41,23 @@ func (b *BeaconState) SetValidators(val []*ethpb.Validator) error {
 func (b *BeaconState) ApplyToEveryValidator(f func(idx int, val *ethpb.Validator) (bool, *ethpb.Validator, error)) error {
 	var changedVals []uint64
 	if features.Get().EnableExperimentalState {
-		b.lock.Lock()
-
 		l := b.validatorsMultiValue.Len(b)
 		for i := 0; i < l; i++ {
 			v, err := b.validatorsMultiValue.At(b, uint64(i))
 			if err != nil {
-				b.lock.Unlock()
 				return err
 			}
 			changed, newVal, err := f(i, v)
 			if err != nil {
-				b.lock.Unlock()
 				return err
 			}
 			if changed {
 				changedVals = append(changedVals, uint64(i))
 				if err = b.validatorsMultiValue.UpdateAt(b, uint64(i), newVal); err != nil {
-					b.lock.Unlock()
 					return errors.Wrapf(err, "could not update validator at index %d", i)
 				}
 			}
 		}
-
-		b.lock.Unlock()
 	} else {
 		b.lock.Lock()
 
```

### beacon-chain/sync/backfill/status_test.go
```diff
@@ -168,9 +168,9 @@ func TestReload(t *testing.T) {
 	require.NoError(t, err)
 
 	cases := []struct {
-		name string
-		db   DB
-		err  error
+		name     string
+		db       DB
+		err      error
 		expected *Status
 	}{
 		/*{
```
