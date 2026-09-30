# [?] Fix Deadlock in Runtime (#8321)

## Summary
Severity: Unknown
Chain: Ethereum
Component: OffchainLabs/prysm
Published: 2021-01-25
Source: https://github.com/OffchainLabs/prysm/commit/7f5ffb7dd1c8e8f5c5498e3f7d44eb53a7aea069
Type: security-commit

## Details
Fix Deadlock in Runtime (#8321)

* fix deadlock

* fix

* Satisfy Deepsource

* fmt

## Patch
### beacon-chain/state/BUILD.bazel
```diff
@@ -50,9 +50,9 @@ go_test(
         "getters_test.go",
         "helpers_test.go",
         "references_test.go",
+        "state_test.go",
         "state_trie_test.go",
         "types_test.go",
-        "validator_map_test.go",
     ],
     embed = [":go_default_library"],
     deps = [
```

### beacon-chain/state/state_test.go
```diff
@@ -0,0 +1,92 @@
+package state
+
+import (
+	"strconv"
+	"sync"
+	"testing"
+
+	ethpb "github.com/prysmaticlabs/ethereumapis/eth/v1alpha1"
+	pb "github.com/prysmaticlabs/prysm/proto/beacon/p2p/v1"
+	"github.com/prysmaticlabs/prysm/shared/bytesutil"
+	"github.com/prysmaticlabs/prysm/shared/params"
+	"github.com/prysmaticlabs/prysm/shared/testutil/assert"
+)
+
+func TestValidatorMap_DistinctCopy(t *testing.T) {
+	count := uint64(100)
+	vals := make([]*ethpb.Validator, 0, count)
+	for i := uint64(1); i < count; i++ {
+		someRoot := [32]byte{}
+		someKey := [48]byte{}
+		copy(someRoot[:], strconv.Itoa(int(i)))
+		copy(someKey[:], strconv.Itoa(int(i)))
+		vals = append(vals, &ethpb.Validator{
+			PublicKey:                  someKey[:],
+			WithdrawalCredentials:      someRoot[:],
+			EffectiveBalance:           params.BeaconConfig().MaxEffectiveBalance,
+			Slashed:                    false,
+			ActivationEligibilityEpoch: 1,
+			ActivationEpoch:            1,
+			ExitEpoch:                  1,
+			WithdrawableEpoch:          1,
+		})
+	}
+	handler := newValHandler(vals)
+	newHandler := handler.copy()
+	wantedPubkey := strconv.Itoa(22)
+	handler.valIdxMap[bytesutil.ToBytes48([]byte(wantedPubkey))] = 27
+	assert.NotEqual(t, handler.valIdxMap[bytesutil.ToBytes48([]byte(wantedPubkey))], newHandler.valIdxMap[bytesutil.ToBytes48([]byte(wantedPubkey))], "Values are supposed to be unequal due to copy")
+}
+
+func TestBeaconState_NoDeadlock(t *testing.T) {
+	count := uint64(100)
+	vals := make([]*ethpb.Validator, 0, count)
+	for i := uint64(1); i < count; i++ {
+		someRoot := [32]byte{}
+		someKey := [48]byte{}
+		copy(someRoot[:], strconv.Itoa(int(i)))
+		copy(someKey[:], strconv.Itoa(int(i)))
+		vals = append(vals, &ethpb.Validator{
+			PublicKey:                  someKey[:],
+			WithdrawalCredentials:      someRoot[:],
+			EffectiveBalance:           params.BeaconConfig().MaxEffectiveBalance,
+			Slashed:                    false,
+			ActivationEligibilityEpoch: 1,
+			ActivationEpoch:            1,
+			ExitEpoch:                  1,
+			WithdrawableEpoch:          1,
+		})
+	}
+	st, err := InitializeFromProtoUnsafe(&pb.BeaconState{
+		Validators: vals,
+	})
+	assert.NoError(t, err)
+	wg := new(sync.WaitGroup)
+
+	wg.Add(1)
+	go func() {
+		// Continuously lock and unlock the state
+		// by acquiring the lock.
+		for i := 0; i < 1000; i++ {
+			for _, f := range st.stateFieldLeaves {
+				f.Lock()
+				if len(f.fieldLayers) == 0 {
+					f.fieldLayers = make([][]*[32]byte, 10)
+				}
+				f.Unlock()
+				f.AddRef()
+			}
+		}
+		wg.Done()
+	}()
+	// Constantly read from the offending portion
+	// of the code to ensure there is no possible
+	// recursive read locking.
+	for i := 0; i < 1000; i++ {
+		go func() {
+			_ = st.FieldReferencesCount()
+		}()
+	}
+	// Test will not terminate in the event of a deadlock.
+	wg.Wait()
+}
```

### beacon-chain/state/state_trie.go
```diff
@@ -213,9 +213,10 @@ func (b *BeaconState) FieldReferencesCount() map[string]uint64 {
 		refMap[i.String()] = uint64(f.Refs())
 	}
 	for i, f := range b.stateFieldLeaves {
+		numOfRefs := uint64(f.Refs())
 		f.lock.RLock()
 		if len(f.fieldLayers) != 0 {
-			refMap[i.String()+"_trie"] = uint64(f.Refs())
+			refMap[i.String()+"_trie"] = numOfRefs
 		}
 		f.lock.RUnlock()
 	}
```

### beacon-chain/state/validator_map_test.go
```diff
@@ -1,37 +0,0 @@
-package state
-
-import (
-	"strconv"
-	"testing"
-
-	ethpb "github.com/prysmaticlabs/ethereumapis/eth/v1alpha1"
-	"github.com/prysmaticlabs/prysm/shared/bytesutil"
-	"github.com/prysmaticlabs/prysm/shared/params"
-	"github.com/prysmaticlabs/prysm/shared/testutil/assert"
-)
-
-func TestValidatorMap_DistinctCopy(t *testing.T) {
-	count := uint64(100)
-	vals := make([]*ethpb.Validator, 0, count)
-	for i := uint64(1); i < count; i++ {
-		someRoot := [32]byte{}
-		someKey := [48]byte{}
-		copy(someRoot[:], strconv.Itoa(int(i)))
-		copy(someKey[:], strconv.Itoa(int(i)))
-		vals = append(vals, &ethpb.Validator{
-			PublicKey:                  someKey[:],
-			WithdrawalCredentials:      someRoot[:],
-			EffectiveBalance:           params.BeaconConfig().MaxEffectiveBalance,
-			Slashed:                    false,
-			ActivationEligibilityEpoch: 1,
-			ActivationEpoch:            1,
-			ExitEpoch:                  1,
-			WithdrawableEpoch:          1,
-		})
-	}
-	handler := newValHandler(vals)
-	newHandler := handler.copy()
-	wantedPubkey := strconv.Itoa(22)
-	handler.valIdxMap[bytesutil.ToBytes48([]byte(wantedPubkey))] = 27
-	assert.NotEqual(t, handler.valIdxMap[bytesutil.ToBytes48([]byte(wantedPubkey))], newHandler.valIdxMap[bytesutil.ToBytes48([]byte(wantedPubkey))], "Values are supposed to be unequal due to copy")
-}
```
