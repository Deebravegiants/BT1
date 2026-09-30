# [?] Builder: fix nil panic edgecase (#12236)

## Summary
Severity: Unknown
Chain: Ethereum
Component: prysmaticlabs/prysm
Published: 2023-04-06
Source: https://github.com/OffchainLabs/prysm/commit/d257ef17424f2c71196688bcb9981c4383dcb2b6
Type: security-commit

## Details
Builder: fix nil panic edgecase (#12236)

* adding fix for buildervalue nil

* fixing linting

* changing based on review comment

* editing based on suggestions

* fixing unit test

* fixing linting

* fall back to local

* fix linting

* updating based on slack feedback

## Patch
### beacon-chain/rpc/prysm/v1alpha1/validator/proposer_bellatrix.go
```diff
@@ -4,6 +4,7 @@ import (
 	"bytes"
 	"context"
 	"fmt"
+	"math/big"
 	"time"
 
 	"github.com/pkg/errors"
@@ -68,6 +69,7 @@ func (vs *Server) setExecutionData(ctx context.Context, blk interfaces.SignedBea
 				v, err = builderPayload.Value()
 				if err != nil {
 					log.WithError(err).Warn("Proposer: failed to get builder payload value") // Default to local if can't get builder value.
+					v = big.NewInt(0)                                                        // Default to local if can't get builder value.
 				}
 				builderValue := v.Uint64()
 
@@ -149,6 +151,9 @@ func (vs *Server) getPayloadHeaderFromBuilder(ctx context.Context, slot primitiv
 	if signedBid.IsNil() {
 		return nil, errors.New("builder returned nil bid")
 	}
+	if signedBid.Version() != b.Version() {
+		return nil, fmt.Errorf("builder bid response version: %d is different from head block version: %d", signedBid.Version(), b.Version())
+	}
 	bid, err := signedBid.Message()
 	if err != nil {
 		return nil, errors.Wrap(err, "could not get bid")
```

### beacon-chain/rpc/prysm/v1alpha1/validator/proposer_bellatrix_test.go
```diff
@@ -172,7 +172,7 @@ func TestServer_setExecutionData(t *testing.T) {
 		vs.BlockBuilder = &builderTest.MockBuilderService{
 			BidCapella: sBid,
 		}
-		wb, err := blocks.NewSignedBeaconBlock(util.NewBeaconBlockBellatrix())
+		wb, err := blocks.NewSignedBeaconBlock(util.NewBeaconBlockCapella())
 		require.NoError(t, err)
 		chain := &blockchainTest.ChainService{ForkChoiceStore: doublylinkedtree.New(), Genesis: time.Now(), Block: wb}
 		vs.ForkFetcher = chain
```
