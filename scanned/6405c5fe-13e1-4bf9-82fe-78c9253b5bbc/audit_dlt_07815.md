# [?] Mitigate potential overflow. ethereum/eth2.0-specs#2129 (#7795)

## Summary
Severity: Unknown
Chain: Ethereum
Component: OffchainLabs/prysm
Published: 2020-11-12
Source: https://github.com/OffchainLabs/prysm/commit/5f9239595b4913ccb0ed5ed77b33cf8499494613
Type: security-commit

## Details
Mitigate potential overflow. ethereum/eth2.0-specs#2129 (#7795)

## Patch
### beacon-chain/core/helpers/block.go
```diff
@@ -1,6 +1,8 @@
 package helpers
 
 import (
+	"math"
+
 	"github.com/pkg/errors"
 	stateTrie "github.com/prysmaticlabs/prysm/beacon-chain/state"
 	"github.com/prysmaticlabs/prysm/shared/params"
@@ -17,6 +19,9 @@ import (
 //    assert slot < state.slot <= slot + SLOTS_PER_HISTORICAL_ROOT
 //    return state.block_roots[slot % SLOTS_PER_HISTORICAL_ROOT]
 func BlockRootAtSlot(state *stateTrie.BeaconState, slot uint64) ([]byte, error) {
+	if math.MaxUint64-slot < params.BeaconConfig().SlotsPerHistoricalRoot {
+		return []byte{}, errors.New("slot overflows uint64")
+	}
 	if slot >= state.Slot() || state.Slot() > slot+params.BeaconConfig().SlotsPerHistoricalRoot {
 		return []byte{}, errors.Errorf("slot %d out of bounds", slot)
 	}
```

### beacon-chain/core/helpers/block_test.go
```diff
@@ -2,6 +2,7 @@ package helpers_test
 
 import (
 	"fmt"
+	"math"
 	"testing"
 
 	"github.com/prysmaticlabs/prysm/beacon-chain/core/helpers"
@@ -101,6 +102,11 @@ func TestBlockRootAtSlot_OutOfBounds(t *testing.T) {
 			stateSlot:   params.BeaconConfig().SlotsPerHistoricalRoot + 2,
 			expectedErr: "slot 1 out of bounds",
 		},
+		{
+			slot:        math.MaxUint64 - 5,
+			stateSlot:   0, // Doesn't matter
+			expectedErr: "slot overflows uint64",
+		},
 	}
 	for _, tt := range tests {
 		state.Slot = tt.stateSlot
```
