# [?] fix: data race on shared *rand.Rand in TestPriorityByGasPrice (#6908)

## Summary
Severity: Unknown
Chain: Celestia
Component: celestiaorg/celestia-app
Published: 2026-03-24
Source: https://github.com/celestiaorg/celestia-app/commit/1b51606e2139b7f3da6c4d4d896bb81006d0b445
Type: security-commit

## Details
fix: data race on shared *rand.Rand in TestPriorityByGasPrice (#6908)

## Summary

- Move `random.New()` inside each goroutine in `TestPriorityByGasPrice`
so each gets its own `*rand.Rand` instance. `math/rand.Rand` is not safe
for concurrent use — sharing one across goroutines caused an `index out
of range [-1]` panic in CI.
- Add `TestManyBlobsConcurrent` regression test to verify concurrent
blob creation with per-goroutine rand instances doesn't panic.

Closes
https://github.com/celestiaorg/celestia-app/actions/runs/23101547657/job/67103056622?pr=6843

## Test plan

- [x] `go vet ./app/test/` passes
- [x] `TestManyBlobsConcurrent` passes with `-race -count=5`

🤖 Generated with [Claude Code](https://claude.com/claude-code)
<!-- devin-review-badge-begin -->

---

<a href="https://app.devin.ai/review/celestiaorg/celestia-app/pull/6908"
target="_blank">
  <picture>
<source media="(prefers-color-scheme: dark)"
srcset="https://static.devin.ai/assets/gh-open-in-devin-review-dark.svg?v=1">
<img
src="https://static.devin.ai/assets/gh-open-in-devin-review-light.svg?v=1"
alt="Open with Devin">
  </picture>
</a>
<!-- devin-review-badge-end -->

Co-authored-by: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

## Patch
### app/test/priority_test.go
```diff
@@ -75,11 +75,11 @@ func (s *PriorityTestSuite) TestPriorityByGasPrice() {
 	require.NoError(t, err)
 	gasLimit := blobtypes.DefaultEstimateGas(msg)
 	wg := &sync.WaitGroup{}
-	r := random.New()
 	for _, accName := range s.accountNames {
 		wg.Go(func() {
 			// ensure that it is greater than the min gas price
 			gasPrice := float64(rand.Intn(1000)+1) * appconsts.DefaultMinGasPrice
+			r := random.New()
 			blobs := blobfactory.ManyBlobs(r, []share.Namespace{share.RandomBlobNamespace()}, []int{100})
 			resp, err := s.txClient.BroadcastPayForBlobWithAccount(
 				s.cctx.GoContext(),
```

### test/util/blobfactory/payforblob_factory_test.go
```diff
@@ -1,6 +1,7 @@
 package blobfactory_test
 
 import (
+	"sync"
 	"testing"
 
 	"github.com/celestiaorg/celestia-app/v8/app"
@@ -9,6 +10,7 @@ import (
 	"github.com/celestiaorg/celestia-app/v8/test/util/random"
 	"github.com/celestiaorg/celestia-app/v8/test/util/testfactory"
 	"github.com/celestiaorg/celestia-app/v8/test/util/testnode"
+	"github.com/celestiaorg/go-square/v4/share"
 	"github.com/cometbft/cometbft/types"
 	"github.com/stretchr/testify/assert"
 	"github.com/stretchr/testify/require"
@@ -55,3 +57,21 @@ func TestRandMultiBlobTxsSameSigner_Deterministic(t *testing.T) {
 
 	assert.Equal(t, marshalledBlobTxs1, marshalledBlobTxs2)
 }
+
+// TestManyBlobsConcurrent verifies that ManyBlobs can be called concurrently
+// without panicking. This is a regression test for a bug where a shared
+// *rand.Rand was passed to ManyBlobs across multiple goroutines, causing a
+// panic due to concurrent access to the non-thread-safe math/rand.Rand.
+func TestManyBlobsConcurrent(t *testing.T) {
+	goroutines := 10
+	wg := &sync.WaitGroup{}
+	for range goroutines {
+		wg.Go(func() {
+			r := random.New()
+			blobs := blobfactory.ManyBlobs(r, []share.Namespace{share.RandomBlobNamespace()}, []int{100})
+			assert.Len(t, blobs, 1)
+			assert.Len(t, blobs[0].Data(), 100)
+		})
+	}
+	wg.Wait()
+}
```
