# [?] overflow bid fix (#17207)

## Summary
Severity: Unknown
Chain: Ethereum
Component: prysmaticlabs/prysm
Published: 2026-07-21
Source: https://github.com/OffchainLabs/prysm/commit/e4d15d741a7acec6e88282155df15bb3a9e83fd9
Type: security-commit

## Details
overflow bid fix (#17207)

**What type of PR is this?**

Bug fix

**What does this PR do? Why is it needed?**

make sure we're protected by overflow

**Which issue(s) does this PR fix?**

Fixes #

**Other notes for review**

**Acknowledgements**

- [x] I have read
[CONTRIBUTING.md](https://github.com/prysmaticlabs/prysm/blob/develop/CONTRIBUTING.md).
- [x] I have included a uniquely named [changelog fragment
file](https://github.com/prysmaticlabs/prysm/blob/develop/CONTRIBUTING.md#maintaining-changelogmd).
- [x] I have added a description with sufficient context for reviewers
to understand this PR.
- [x] I have tested that my changes work as expected and I added a
testing plan to the PR description (if applicable).

## Patch
### beacon-chain/rpc/prysm/v1alpha1/validator/proposer_bid.go
```diff
@@ -3,6 +3,7 @@ package validator
 import (
 	"context"
 	"fmt"
+	"math"
 	"strings"
 	"time"
 
@@ -132,7 +133,11 @@ func effectiveBidValue(bid *ethpb.SignedExecutionPayloadBid, maxExecutionPayment
 	if uint64(payment) > maxExecutionPayment {
 		payment = primitives.Gwei(maxExecutionPayment)
 	}
-	return bid.Message.Value + payment
+	sum := bid.Message.Value + payment
+	if sum < bid.Message.Value {
+		return primitives.Gwei(math.MaxUint64)
+	}
+	return sum
 }
 
 // builderBidQuery carries the proposal context builder bids are requested and validated against.
```

### beacon-chain/rpc/prysm/v1alpha1/validator/proposer_bid_builder_test.go
```diff
@@ -3,6 +3,7 @@
 package validator
 
 import (
+	"math"
 	"math/big"
 	"testing"
 
@@ -87,6 +88,8 @@ func TestEffectiveBidValue(t *testing.T) {
 		{"payment over cap is capped", 1000, 900, 500, 1500},
 		{"zero payment", 1000, 0, 500, 1000},
 		{"zero cap ignores payment", 1000, 900, 0, 1000},
+		{"sum past uint64 saturates", math.MaxUint64 - 5, 100, math.MaxUint64, math.MaxUint64},
+		{"max value zero payment unchanged", math.MaxUint64, 0, math.MaxUint64, math.MaxUint64},
 	}
 	for _, tt := range tests {
 		t.Run(tt.name, func(t *testing.T) {
@@ -119,6 +122,7 @@ func TestBestBid(t *testing.T) {
 		{name: "tie prefers p2p", local: localWithGwei(0), p2p: newBid(1000, 0, p2pIdx), builder: newBid(1000, 0, builderIdx), maxPayment: 1000, wantSrc: bidSourceP2P},
 		{name: "payment cap keeps local ahead", local: localWithGwei(100), builder: newBid(50, 100, builderIdx), maxPayment: 40, wantSrc: bidSourceSelfBuild, wantNil: true},
 		{name: "payment within cap wins", local: localWithGwei(100), builder: newBid(50, 100, builderIdx), maxPayment: 60, wantSrc: bidSourceBuilderAPI},
+		{name: "saturated bid still beats local", local: localWithGwei(100), builder: newBid(math.MaxUint64-5, 100, builderIdx), maxPayment: math.MaxUint64, wantSrc: bidSourceBuilderAPI},
 	}
 	for _, tt := range tests {
 		t.Run(tt.name, func(t *testing.T) {
```

### changelog/james-prysm_saturate-effective-bid-value.md
```diff
@@ -0,0 +1,3 @@
+### Fixed
+
+- Use saturating arithmetic when computing the effective bid value during Gloas bid selection.
```
