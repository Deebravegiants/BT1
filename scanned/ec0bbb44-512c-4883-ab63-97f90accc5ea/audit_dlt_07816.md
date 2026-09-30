# [?] Prevent Panics in Field Trie Helpers (#7613)

## Summary
Severity: Unknown
Chain: Ethereum
Component: OffchainLabs/prysm
Published: 2020-10-23
Source: https://github.com/OffchainLabs/prysm/commit/b1c047b9ee8661d2888042d95f93f898a7bf1ede
Type: security-commit

## Details
Prevent Panics in Field Trie Helpers (#7613)

* add tests to prevent panics

* if > 0

* fix typ

## Patch
### beacon-chain/state/BUILD.bazel
```diff
@@ -49,6 +49,7 @@ go_test(
     srcs = [
         "field_trie_test.go",
         "getters_test.go",
+        "helpers_test.go",
         "references_test.go",
         "state_trie_test.go",
         "types_test.go",
```

### beacon-chain/state/field_trie.go
```diff
@@ -1,6 +1,7 @@
 package state
 
 import (
+	"fmt"
 	"reflect"
 	"sync"
 
@@ -180,18 +181,23 @@ func handleByteArrays(val [][]byte, indices []uint64, convertAll bool) ([][32]by
 		length = len(val)
 	}
 	roots := make([][32]byte, 0, length)
-	rootCreater := func(input []byte) {
+	rootCreator := func(input []byte) {
 		newRoot := bytesutil.ToBytes32(input)
 		roots = append(roots, newRoot)
 	}
 	if convertAll {
 		for i := range val {
-			rootCreater(val[i])
+			rootCreator(val[i])
 		}
 		return roots, nil
 	}
-	for _, idx := range indices {
-		rootCreater(val[idx])
+	if len(val) > 0 {
+		for _, idx := range indices {
+			if idx > uint64(len(val))-1 {
+				return nil, fmt.Errorf("index %d greater than number of byte arrays %d", idx, len(val))
+			}
+			rootCreator(val[idx])
+		}
 	}
 	return roots, nil
 }
@@ -203,7 +209,7 @@ func handleEth1DataSlice(val []*ethpb.Eth1Data, indices []uint64, convertAll boo
 	}
 	roots := make([][32]byte, 0, length)
 	hasher := hashutil.CustomSHA256Hasher()
-	rootCreater := func(input *ethpb.Eth1Data) error {
+	rootCreator := func(input *ethpb.Eth1Data) error {
 		newRoot, err := stateutil.Eth1Root(hasher, input)
 		if err != nil {
 			return err
@@ -213,17 +219,22 @@ func handleEth1DataSlice(val []*ethpb.Eth1Data, indices []uint64, convertAll boo
 	}
 	if convertAll {
 		for i := range val {
-			err := rootCreater(val[i])
+			err := rootCreator(val[i])
 			if err != nil {
 				return nil, err
 			}
 		}
 		return roots, nil
 	}
-	for _, idx := range indices {
-		err := rootCreater(val[idx])
-		if err != nil {
-			return nil, err
+	if len(val) > 0 {
+		for _, idx := range indices {
+			if idx > uint64(len(val))-1 {
+				return nil, fmt.Errorf("index %d greater than number of items in eth1 data slice %d", idx, len(val))
+			}
+			err := rootCreator(val[idx])
+			if err != nil {
+				return nil, err
+			}
 		}
 	}
 	return roots, nil
@@ -236,7 +247,7 @@ func handleValidatorSlice(val []*ethpb.Validator, indices []uint64, convertAll b
 	}
 	roots := make([][32]byte, 0, length)
 	hasher := hashutil.CustomSHA256Hasher()
-	rootCreater := func(input *ethpb.Validator) error {
+	rootCreator := func(input *ethpb.Validator) error {
 		newRoot, err := stateutil.ValidatorRoot(hasher, input)
 		if err != nil {
 			return err
@@ -246,17 +257,22 @@ func handleValidatorSlice(val []*ethpb.Validator, indices []uint64, convertAll b
 	}
 	if convertAll {
 		for i := range val {
-			err := rootCreater(val[i])
+			err := rootCreator(val[i])
 			if err != nil {
 				return nil, err
 			}
 		}
 		return roots, nil
 	}
-	for _, idx := range indices {
-		err := rootCreater(val[idx])
-		if err != nil {
-			return nil, err
+	if len(val) > 0 {
+		for _, idx := range indices {
+			if idx > uint64(len(val))-1 {
+				return nil, fmt.Errorf("index %d greater than number of validators %d", idx, len(val))
+			}
+			err := rootCreator(val[idx])
+			if err != nil {
+				return nil, err
+			}
 		}
 	}
 	return roots, nil
@@ -286,10 +302,15 @@ func handlePendingAttestation(val []*pb.PendingAttestation, indices []uint64, co
 		}
 		return roots, nil
 	}
-	for _, idx := range indices {
-		err := rootCreator(val[idx])
-		if err != nil {
-			return nil, err
+	if len(val) > 0 {
+		for _, idx := range indices {
+			if idx > uint64(len(val))-1 {
+				return nil, fmt.Errorf("index %d greater than number of pending attestations %d", idx, len(val))
+			}
+			err := rootCreator(val[idx])
+			if err != nil {
+				return nil, err
+			}
 		}
 	}
 	return roots, nil
```

### beacon-chain/state/helpers_test.go
```diff
@@ -0,0 +1,30 @@
+package state
+
+import (
+	"testing"
+
+	ethpb "github.com/prysmaticlabs/ethereumapis/eth/v1alpha1"
+	pb "github.com/prysmaticlabs/prysm/proto/beacon/p2p/v1"
+	"github.com/prysmaticlabs/prysm/shared/testutil/assert"
+)
+
+func Test_handleValidatorSlice_OutOfRange(t *testing.T) {
+	vals := make([]*ethpb.Validator, 1)
+	indices := []uint64{3}
+	_, err := handleValidatorSlice(vals, indices, false)
+	assert.ErrorContains(t, "index 3 greater than number of validators 1", err)
+}
+
+func Test_handlePendingAttestation_OutOfRange(t *testing.T) {
+	items := make([]*pb.PendingAttestation, 1)
+	indices := []uint64{3}
+	_, err := handlePendingAttestation(items, indices, false)
+	assert.ErrorContains(t, "index 3 greater than number of pending attestations 1", err)
+}
+
+func Test_handleEth1DataSlice_OutOfRange(t *testing.T) {
+	items := make([]*ethpb.Eth1Data, 1)
+	indices := []uint64{3}
+	_, err := handleEth1DataSlice(items, indices, false)
+	assert.ErrorContains(t, "index 3 greater than number of items in eth1 data slice 1", err)
+}
```
