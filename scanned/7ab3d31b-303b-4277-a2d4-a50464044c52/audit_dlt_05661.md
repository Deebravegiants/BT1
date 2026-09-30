# [?] sync: fix KZG batch verifier deadlock on timeout (#16141)

## Summary
Severity: Unknown
Chain: Ethereum
Component: prysmaticlabs/prysm
Published: 2025-12-12
Source: https://github.com/OffchainLabs/prysm/commit/096cba5b2d597d9ce8d3160b4351177de29b2d63
Type: security-commit

## Details
sync: fix KZG batch verifier deadlock on timeout (#16141)

`validateWithKzgBatchVerifier` could timeout (12s) and once it times out
because `resChan` is unbuffered, the verifier will stuck at following
line at `verifyKzgBatch` as its waiting for someone to grab the result
from `resChan`:
```
	for _, verifier := range kzgBatch {
		verifier.resChan <- verificationErr
	}
```
Fix is to make kzg batch verification non blocking on timeouts by
buffering each request’s buffered size 1

## Patch
### beacon-chain/sync/batch_verifier.go
```diff
@@ -161,7 +161,7 @@ func (s *Service) validateWithKzgBatchVerifier(ctx context.Context, dataColumns
 
 	timeout := time.Duration(params.BeaconConfig().SecondsPerSlot) * time.Second
 
-	resChan := make(chan error)
+	resChan := make(chan error, 1)
 	verificationSet := &kzgVerifier{dataColumns: dataColumns, resChan: resChan}
 	s.kzgChan <- verificationSet
 
```

### beacon-chain/sync/kzg_batch_verifier_test.go
```diff
@@ -7,6 +7,7 @@ import (
 	"time"
 
 	"github.com/OffchainLabs/prysm/v7/beacon-chain/blockchain/kzg"
+	"github.com/OffchainLabs/prysm/v7/config/params"
 	"github.com/OffchainLabs/prysm/v7/consensus-types/blocks"
 	ethpb "github.com/OffchainLabs/prysm/v7/proto/prysm/v1alpha1"
 	"github.com/OffchainLabs/prysm/v7/testing/assert"
@@ -268,6 +269,41 @@ func TestKzgBatchVerifierFallback(t *testing.T) {
 	})
 }
 
+func TestValidateWithKzgBatchVerifier_DeadlockOnTimeout(t *testing.T) {
+	err := kzg.Start()
+	require.NoError(t, err)
+
+	params.SetupTestConfigCleanup(t)
+	cfg := params.BeaconConfig().Copy()
+	cfg.SecondsPerSlot = 0
+	params.OverrideBeaconConfig(cfg)
+
+	ctx, cancel := context.WithCancel(t.Context())
+	defer cancel()
+
+	service := &Service{
+		ctx:     ctx,
+		kzgChan: make(chan *kzgVerifier),
+	}
+	go service.kzgVerifierRoutine()
+
+	result, err := service.validateWithKzgBatchVerifier(context.Background(), nil)
+	require.Equal(t, pubsub.ValidationIgnore, result)
+	require.ErrorIs(t, err, context.DeadlineExceeded)
+
+	done := make(chan struct{})
+	go func() {
+		_, _ = service.validateWithKzgBatchVerifier(context.Background(), nil)
+		close(done)
+	}()
+
+	select {
+	case <-done:
+	case <-time.After(500 * time.Millisecond):
+		t.Fatal("validateWithKzgBatchVerifier blocked")
+	}
+}
+
 func createValidTestDataColumns(t *testing.T, count int) []blocks.RODataColumn {
 	_, roSidecars, _ := util.GenerateTestFuluBlockWithSidecars(t, count)
 	if len(roSidecars) >= count {
```

### changelog/fix_kzg_batch_verifier_timeout_deadlock.md
```diff
@@ -0,0 +1,3 @@
+### Fixed
+
+- Fix deadlock in data column gossip KZG batch verification when a caller times out preventing result delivery.
```
