# [?] eth: fix overflow impacting milestone lock and syncing (#2111)

## Summary
Severity: Unknown
Chain: Polygon
Component: 0xPolygon/bor
Published: 2026-03-05
Source: https://github.com/0xPolygon/bor/commit/27130c242a5782760a4a6c128558c07802d0907a
Type: security-commit

## Details
eth: fix overflow impacting milestone lock and syncing (#2111)

* eth: fix overflow impacting milestone lock and syncing

* eth: address comments

## Patch
### cmd/keeper/go.mod
```diff
@@ -51,6 +51,7 @@ require (
 	golang.org/x/crypto v0.46.0 // indirect
 	golang.org/x/sync v0.19.0 // indirect
 	golang.org/x/sys v0.40.0 // indirect
+	golang.org/x/time v0.12.0 // indirect
 	gopkg.in/yaml.v2 v2.4.0 // indirect
 )
 
```

### cmd/keeper/go.sum
```diff
@@ -170,6 +170,7 @@ golang.org/x/sys v0.39.0/go.mod h1:OgkHotnGiDImocRcuBABYBEXf8A9a87e/uXjp9XT3ks=
 golang.org/x/sys v0.40.0/go.mod h1:OgkHotnGiDImocRcuBABYBEXf8A9a87e/uXjp9XT3ks=
 golang.org/x/text v0.32.0 h1:ZD01bjUt1FQ9WJ0ClOL5vxgxOI/sVCNgX1YtKwcY0mU=
 golang.org/x/text v0.32.0/go.mod h1:o/rUWzghvpD5TXrTIBuJU77MTaN0ljMWE47kxGJQ7jY=
+golang.org/x/time v0.12.0/go.mod h1:CDIdPxbZBQxdj6cxyCIdrNogrJKMJ7pr37NYpMcMDSg=
 google.golang.org/protobuf v1.36.10 h1:AYd7cD/uASjIL6Q9LiTjz8JLcrh/88q5UObnmY3aOOE=
 google.golang.org/protobuf v1.36.10/go.mod h1:HTf+CrKn2C3g5S8VImy6tdcUvCska2kB7j23XfzDpco=
 gopkg.in/check.v1 v0.0.0-20161208181325-20d25e280405/go.mod h1:Co6ibVJAznAaIkqp8huTwlJQCZ016jof/cbN4VW5Yz0=
```

### eth/bor_api_backend.go
```diff
@@ -4,6 +4,7 @@ import (
 	"context"
 	"errors"
 	"fmt"
+	"math"
 
 	"github.com/ethereum/go-ethereum"
 	"github.com/ethereum/go-ethereum/common"
@@ -16,10 +17,15 @@ import (
 	"github.com/ethereum/go-ethereum/rpc"
 )
 
-var errBorEngineNotAvailable error = errors.New("Only available in Bor engine")
+const tipConfirmationOffset uint64 = 16
+
+var (
+	errBorEngineNotAvailable = errors.New("Only available in Bor engine")
+	errInvalidBlockNumber    = errors.New("end block number is out of safe range")
+)
 
 // GetRootHash returns root hash for given start and end block
-func (b *EthAPIBackend) GetRootHash(ctx context.Context, starBlockNr uint64, endBlockNr uint64) (string, error) {
+func (b *EthAPIBackend) GetRootHash(_ context.Context, starBlockNr uint64, endBlockNr uint64) (string, error) {
 	var api *bor.API
 
 	for _, _api := range b.eth.Engine().APIs(b.eth.BlockChain()) {
@@ -41,7 +47,12 @@ func (b *EthAPIBackend) GetRootHash(ctx context.Context, starBlockNr uint64, end
 }
 
 // GetVoteOnHash returns the vote on hash
-func (b *EthAPIBackend) GetVoteOnHash(ctx context.Context, starBlockNr uint64, endBlockNr uint64, hash string, milestoneId string) (bool, error) {
+func (b *EthAPIBackend) GetVoteOnHash(ctx context.Context, _ uint64, endBlockNr uint64, hash string, milestoneId string) (bool, error) {
+	// Reject invalid block numbers (overflowing with the confirmation offset or exceeding the valid range).
+	if endBlockNr > math.MaxInt64-tipConfirmationOffset {
+		return false, errInvalidBlockNumber
+	}
+
 	var api *bor.API
 
 	for _, _api := range b.eth.Engine().APIs(b.eth.BlockChain()) {
@@ -54,16 +65,16 @@ func (b *EthAPIBackend) GetVoteOnHash(ctx context.Context, starBlockNr uint64, e
 		return false, errBorEngineNotAvailable
 	}
 
-	// Confirmation of 16 blocks on the endblock
-	tipConfirmationBlockNr := endBlockNr + uint64(16)
+	// Confirmation of tipConfirmationOffset blocks on the endblock
+	tipConfirmationBlockNr := endBlockNr + tipConfirmationOffset
 
-	// Check if tipConfirmation block exit
-	_, err := b.BlockByNumber(ctx, rpc.BlockNumber(tipConfirmationBlockNr))
-	if err != nil {
+	// Check if the tipConfirmation block exists
+	tipBlock, err := b.BlockByNumber(ctx, rpc.BlockNumber(tipConfirmationBlockNr))
+	if err != nil || tipBlock == nil {
 		return false, errTipConfirmationBlock
 	}
 
-	// Check if end block exist
+	// Check if the end block exists
 	localEndBlock, err := b.BlockByNumber(ctx, rpc.BlockNumber(endBlockNr))
 	if err != nil || localEndBlock == nil {
 		return false, errEndBlock
```

### eth/bor_api_backend_test.go
```diff
@@ -0,0 +1,61 @@
+package eth
+
+import (
+	"context"
+	"errors"
+	"math"
+	"testing"
+)
+
+// TestGetVoteOnHashRejectsOutOfRangeBlockNumbers verifies that GetVoteOnHash returns an error when endBlockNr is outside the safe range.
+func TestGetVoteOnHashRejectsOutOfRangeBlockNumbers(t *testing.T) {
+	t.Parallel()
+
+	backend := &EthAPIBackend{}
+
+	rejectCases := []struct {
+		name       string
+		endBlockNr uint64
+	}{
+		{"max uint64", math.MaxUint64},
+		{"max uint64 minus 15", math.MaxUint64 - 15},
+		{"max int64", math.MaxInt64},
+		{"max int64 minus 15", math.MaxInt64 - 15},
+	}
+
+	for _, tt := range rejectCases {
+		t.Run(tt.name, func(t *testing.T) {
+			t.Parallel()
+
+			_, err := backend.GetVoteOnHash(context.Background(), 0, tt.endBlockNr, "0x00", "test")
+			if err == nil {
+				t.Fatalf("expected error for endBlockNr=%d, got nil", tt.endBlockNr)
+			}
+			if !errors.Is(err, errInvalidBlockNumber) {
+				t.Fatalf("expected errInvalidBlockNumber, got %v", err)
+			}
+		})
+	}
+
+	// Boundary value: math.MaxInt64 - tipConfirmationOffset is the highest accepted endBlockNr.
+	// The call passes the range guard and then panics on nil backend internals,
+	// which confirms the guard did not reject it.
+	t.Run("max int64 minus tipConfirmationOffset (boundary, should pass guard)", func(t *testing.T) {
+		t.Parallel()
+
+		defer func() {
+			if r := recover(); r == nil {
+				// No panic means the function returned normally — check that
+				// the error is not errInvalidBlockNumber.
+			}
+			// A panic here means the boundary value passed the guard and
+			// proceeded into backend logic (which is nil in this test). That's
+			// the expected outcome.
+		}()
+
+		_, err := backend.GetVoteOnHash(context.Background(), 0, math.MaxInt64-tipConfirmationOffset, "0x00", "test")
+		if errors.Is(err, errInvalidBlockNumber) {
+			t.Fatal("expected boundary value to pass the range check, but got errInvalidBlockNumber")
+		}
+	})
+}
```

### eth/downloader/whitelist/milestone_test.go
```diff
@@ -1,6 +1,7 @@
 package whitelist
 
 import (
+	"math"
 	"math/big"
 	"sync"
 	"sync/atomic"
@@ -59,6 +60,66 @@ func TestUnlockSprintThreshold(t *testing.T) {
 	m.finality.RUnlock()
 }
 
+// TestIsReorgAllowedWithMaxLockedNumber verifies that IsReorgAllowed correctly
+// handles the case where LockedMilestoneNumber is set to an extremely large value.
+// No real chain tip can exceed such a number, so IsReorgAllowed must return false.
+func TestIsReorgAllowedWithMaxLockedNumber(t *testing.T) {
+	db := rawdb.NewMemoryDatabase()
+	svc := NewService(db, false, 0)
+
+	m, ok := svc.milestoneService.(*milestone)
+	if !ok {
+		t.Fatalf("expected milestoneService to be *milestone, got %T", svc.milestoneService)
+	}
+
+	chain := []*types.Header{
+		{Number: new(big.Int).SetUint64(100)},
+		{Number: new(big.Int).SetUint64(200)},
+		{Number: new(big.Int).SetUint64(300)},
+	}
+
+	// With a normal locked milestone below the chain tip and not in the chain, reorg is allowed
+	if !m.IsReorgAllowed(chain, 50, common.Hash{}) {
+		t.Fatal("expected reorg to be allowed when chain tip exceeds locked milestone not in chain")
+	}
+
+	// With max uint64 as the locked milestone, no chain tip can exceed it, so the reorg is blocked
+	if m.IsReorgAllowed(chain, math.MaxUint64, common.Hash{}) {
+		t.Fatal("expected reorg to be blocked when locked milestone is max uint64")
+	}
+}
+
+// TestIsValidChainWithMaxLockedNumber verifies that a milestone locked at an
+// unreachable block number causes IsValidChain to reject all chains.
+func TestIsValidChainWithMaxLockedNumber(t *testing.T) {
+	db := rawdb.NewMemoryDatabase()
+	svc := NewService(db, false, 0)
+
+	m, ok := svc.milestoneService.(*milestone)
+	if !ok {
+		t.Fatalf("expected milestoneService to be *milestone, got %T", svc.milestoneService)
+	}
+
+	chain := []*types.Header{
+		{Number: new(big.Int).SetUint64(100)},
+		{Number: new(big.Int).SetUint64(200)},
+	}
+	currentHeader := chain[len(chain)-1]
+
+	// Set locked milestone to max uint64 under write lock
+	m.finality.Lock()
+	m.Locked = true
+	m.LockedMilestoneNumber = math.MaxUint64
+	m.LockedMilestoneHash = common.Hash{0x01}
+	m.LockedMilestoneIDs = map[string]struct{}{"test": {}}
+	m.finality.Unlock()
+
+	valid, _ := m.IsValidChain(currentHeader, chain)
+	if valid {
+		t.Fatal("expected chain to be invalid when locked milestone number is max uint64")
+	}
+}
+
 // TestMilestoneUnlockSprintRace exercises concurrent readers and writers
 // of milestone lock state and future milestone lists.
 //
```

### eth/downloader/whitelist/service.go
```diff
@@ -3,6 +3,7 @@ package whitelist
 import (
 	"errors"
 	"fmt"
+	"math"
 	"sync"
 
 	"github.com/ethereum/go-ethereum/common"
@@ -78,6 +79,19 @@ func NewService(db ethdb.Database, disableBlindForkValidation bool, maxBlindFork
 		lockedMilestoneIDs = make(map[string]struct{})
 	}
 
+	// Discard the locked state if the stored milestone number is out of the safe range (corrupted data).
+	if locked && lockedMilestoneNumber > math.MaxInt64 {
+		log.Warn("Discarding invalid locked milestone loaded from DB", "lockedMilestoneNumber", lockedMilestoneNumber)
+		locked = false
+		lockedMilestoneNumber = 0
+		lockedMilestoneHash = common.Hash{}
+		lockedMilestoneIDs = make(map[string]struct{})
+
+		if err := rawdb.WriteLockField(db, locked, lockedMilestoneNumber, lockedMilestoneHash, lockedMilestoneIDs); err != nil {
+			log.Error("Error clearing invalid lock data from db", "err", err)
+		}
+	}
+
 	order, list, err := rawdb.ReadFutureMilestoneList(db)
 	if err != nil {
 		order = make([]uint64, 0)
```

### eth/downloader/whitelist/service_test.go
```diff
@@ -4,6 +4,7 @@ package whitelist
 import (
 	"errors"
 	"fmt"
+	"math"
 	"math/big"
 	"reflect"
 	"sort"
@@ -1533,3 +1534,61 @@ func TestForkCorrectness(t *testing.T) {
 		require.Equal(t, chain3[1].Number.Uint64(), s.lastValidForkBlock, "expected last known valid block to be unchanged")
 	})
 }
+
+// TestNewServiceDiscardsInvalidLockedMilestone verifies that NewService detects and clears
+// a LockedMilestoneNumber that is beyond the safe range when loading from DB.
+func TestNewServiceDiscardsInvalidLockedMilestone(t *testing.T) {
+	db := rawdb.NewMemoryDatabase()
+
+	// Write a locked milestone with an unreachable block number to the DB,
+	// simulating a previously corrupted state.
+	lockedIDs := map[string]struct{}{"bad-id": {}}
+	err := rawdb.WriteLockField(db, true, math.MaxUint64, common.Hash{0xAB}, lockedIDs)
+	require.NoError(t, err)
+
+	// NewService should detect the out-of-range value and clear it.
+	svc := NewService(db, false, 0)
+
+	m, ok := svc.milestoneService.(*milestone)
+	require.True(t, ok)
+
+	m.finality.RLock()
+	defer m.finality.RUnlock()
+
+	require.False(t, m.Locked, "expected Locked to be false after discarding invalid milestone")
+	require.Equal(t, uint64(0), m.LockedMilestoneNumber, "expected LockedMilestoneNumber to be reset to 0")
+	require.Equal(t, common.Hash{}, m.LockedMilestoneHash, "expected LockedMilestoneHash to be reset")
+	require.Empty(t, m.LockedMilestoneIDs, "expected LockedMilestoneIDs to be cleared")
+
+	// Verify the corrected state was persisted to DB.
+	locked, lockedNum, lockedHash, ids, err := rawdb.ReadLockField(db)
+	require.NoError(t, err)
+	require.False(t, locked)
+	require.Equal(t, uint64(0), lockedNum)
+	require.Equal(t, common.Hash{}, lockedHash)
+	require.Empty(t, ids)
+}
+
+// TestNewServicePreservesValidLockedMilestone verifies that NewService does not
+// interfere with a legitimate locked milestone stored in DB.
+func TestNewServicePreservesValidLockedMilestone(t *testing.T) {
+	db := rawdb.NewMemoryDatabase()
+
+	expectedHash := common.Hash{0x42}
+	lockedIDs := map[string]struct{}{"valid-id": {}}
+	err := rawdb.WriteLockField(db, true, 1000, expectedHash, lockedIDs)
+	require.NoError(t, err)
+
+	svc := NewService(db, false, 0)
+
+	m, ok := svc.milestoneService.(*milestone)
+	require.True(t, ok)
+
+	m.finality.RLock()
+	defer m.finality.RUnlock()
+
+	require.True(t, m.Locked, "expected Locked to remain true for valid milestone")
+	require.Equal(t, uint64(1000), m.LockedMilestoneNumber)
+	require.Equal(t, expectedHash, m.LockedMilestoneHash)
+	require.Len(t, m.LockedMilestoneIDs, 1)
+}
```
