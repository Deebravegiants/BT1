# [?] Fix withdrawal epoch overflows (#10739)

## Summary
Severity: Unknown
Chain: Ethereum
Component: OffchainLabs/prysm
Published: 2022-05-23
Source: https://github.com/OffchainLabs/prysm/commit/46c0579816c22d753d6b91687717fb4c2ca26b0c
Type: security-commit

## Details
Fix withdrawal epoch overflows (#10739)

* Fix withdrawal epoch overflows

* Fix typo, used epoch instead of churn

## Patch
### beacon-chain/core/validators/BUILD.bazel
```diff
@@ -16,6 +16,7 @@ go_library(
         "//consensus-types/primitives:go_default_library",
         "//proto/prysm/v1alpha1:go_default_library",
         "//time/slots:go_default_library",
+        "@com_github_ethereum_go_ethereum//common/math:go_default_library",
         "@com_github_pkg_errors//:go_default_library",
     ],
 )
```

### beacon-chain/core/validators/validator.go
```diff
@@ -7,6 +7,7 @@ package validators
 import (
 	"context"
 
+	"github.com/ethereum/go-ethereum/common/math"
 	"github.com/pkg/errors"
 	"github.com/prysmaticlabs/prysm/beacon-chain/core/helpers"
 	"github.com/prysmaticlabs/prysm/beacon-chain/core/time"
@@ -72,7 +73,11 @@ func InitiateValidatorExit(ctx context.Context, s state.BeaconState, idx types.V
 	exitQueueChurn := uint64(0)
 	err = s.ReadFromEveryValidator(func(idx int, val state.ReadOnlyValidator) error {
 		if val.ExitEpoch() == exitQueueEpoch {
-			exitQueueChurn++
+			overflows := false
+			exitQueueChurn, overflows = math.SafeAdd(exitQueueChurn, 1)
+			if overflows {
+				return errors.New("exit queue churn overflows")
+			}
 		}
 		return nil
 	})
@@ -89,10 +94,16 @@ func InitiateValidatorExit(ctx context.Context, s state.BeaconState, idx types.V
 	}
 
 	if exitQueueChurn >= churn {
-		exitQueueEpoch++
+		exitQueueEpoch, err = exitQueueEpoch.SafeAdd(1)
+		if err != nil {
+			return nil, err
+		}
 	}
 	validator.ExitEpoch = exitQueueEpoch
-	validator.WithdrawableEpoch = exitQueueEpoch + params.BeaconConfig().MinValidatorWithdrawabilityDelay
+	validator.WithdrawableEpoch, err = exitQueueEpoch.SafeAddEpoch(params.BeaconConfig().MinValidatorWithdrawabilityDelay)
+	if err != nil {
+		return nil, err
+	}
 	if err := s.UpdateValidatorAtIndex(idx, validator); err != nil {
 		return nil, err
 	}
```

### beacon-chain/core/validators/validator_test.go
```diff
@@ -99,6 +99,17 @@ func TestInitiateValidatorExit_ChurnOverflow(t *testing.T) {
 	assert.Equal(t, wantedEpoch, v.ExitEpoch, "Exit epoch did not cover overflow case")
 }
 
+func TestInitiateValidatorExit_WithdrawalOverflows(t *testing.T) {
+	base := &ethpb.BeaconState{Validators: []*ethpb.Validator{
+		{ExitEpoch: params.BeaconConfig().FarFutureEpoch - 1},
+		{EffectiveBalance: params.BeaconConfig().EjectionBalance, ExitEpoch: params.BeaconConfig().FarFutureEpoch},
+	}}
+	state, err := v1.InitializeFromProto(base)
+	require.NoError(t, err)
+	_, err = InitiateValidatorExit(context.Background(), state, 1)
+	require.ErrorContains(t, "addition overflows", err)
+}
+
 func TestSlashValidator_OK(t *testing.T) {
 	validatorCount := 100
 	registry := make([]*ethpb.Validator, 0, validatorCount)
```

### testing/spectest/shared/altair/epoch_processing/registry_updates.go
```diff
@@ -27,8 +27,6 @@ func RunRegistryUpdatesTests(t *testing.T, config string) {
 	}
 }
 
-func processRegistryUpdatesWrapper(t *testing.T, state state.BeaconState) (state.BeaconState, error) {
-	state, err := epoch.ProcessRegistryUpdates(context.Background(), state)
-	require.NoError(t, err, "Could not process registry updates")
-	return state, nil
+func processRegistryUpdatesWrapper(_ *testing.T, state state.BeaconState) (state.BeaconState, error) {
+	return epoch.ProcessRegistryUpdates(context.Background(), state)
 }
```

### testing/spectest/shared/bellatrix/epoch_processing/registry_updates.go
```diff
@@ -27,8 +27,6 @@ func RunRegistryUpdatesTests(t *testing.T, config string) {
 	}
 }
 
-func processRegistryUpdatesWrapper(t *testing.T, state state.BeaconState) (state.BeaconState, error) {
-	state, err := epoch.ProcessRegistryUpdates(context.Background(), state)
-	require.NoError(t, err, "Could not process registry updates")
-	return state, nil
+func processRegistryUpdatesWrapper(_ *testing.T, state state.BeaconState) (state.BeaconState, error) {
+	return epoch.ProcessRegistryUpdates(context.Background(), state)
 }
```

### testing/spectest/shared/phase0/epoch_processing/registry_updates.go
```diff
@@ -27,8 +27,6 @@ func RunRegistryUpdatesTests(t *testing.T, config string) {
 	}
 }
 
-func processRegistryUpdatesWrapper(t *testing.T, state state.BeaconState) (state.BeaconState, error) {
-	state, err := epoch.ProcessRegistryUpdates(context.Background(), state)
-	require.NoError(t, err, "Could not process registry updates")
-	return state, nil
+func processRegistryUpdatesWrapper(_ *testing.T, state state.BeaconState) (state.BeaconState, error) {
+	return epoch.ProcessRegistryUpdates(context.Background(), state)
 }
```
