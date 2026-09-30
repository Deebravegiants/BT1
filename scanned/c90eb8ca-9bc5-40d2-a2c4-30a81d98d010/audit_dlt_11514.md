# [?] fix(proof): return error instead of panicking on malformed query data (#7206)

## Summary
Severity: Unknown
Chain: Celestia
Component: celestiaorg/celestia-app
Published: 2026-05-04
Source: https://github.com/celestiaorg/celestia-app/commit/08259c0c2971448702c8bcdeffd4a569b4a12686
Type: security-commit

## Details
fix(proof): return error instead of panicking on malformed query data (#7206)

## Summary

- Replace the `panic` in `QueryTxInclusionProof` with an error return so
deserialization failures of attacker-controlled query data are handled
the same way the surrounding `pbb.Unmarshal` failure already is.
- Add a regression test that exercises `QueryTxInclusionProof` with nil,
empty, garbage, and empty-block-proto inputs and asserts no panic.

Closes https://linear.app/celestia/issue/PROTOCO-1671

## Test plan

- [x] `go test -v -run TestQueryTxInclusionProof ./pkg/proof/` passes
- [x] `go build ./...`

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-authored-by: Claude Opus 4.7 (1M context) <noreply@anthropic.com>

## Patch
### pkg/proof/proof_test.go
```diff
@@ -15,6 +15,7 @@ import (
 	square "github.com/celestiaorg/go-square/v4"
 	"github.com/celestiaorg/go-square/v4/share"
 	abci "github.com/cometbft/cometbft/abci/types"
+	tmproto "github.com/cometbft/cometbft/proto/tendermint/types"
 	sdk "github.com/cosmos/cosmos-sdk/types"
 	"github.com/stretchr/testify/assert"
 	"github.com/stretchr/testify/require"
@@ -263,6 +264,26 @@ func TestAllSharesInclusionProof(t *testing.T) {
 	assert.NoError(t, proof.Validate(dataRoot))
 }
 
+// TestQueryTxInclusionProof_DoesNotPanicOnMalformedData ensures the handler
+// returns errors (rather than panicking) when given inputs that look like a
+// proto-block but trigger error paths in downstream parsing.
+func TestQueryTxInclusionProof_DoesNotPanicOnMalformedData(t *testing.T) {
+	emptyBlockBytes, err := (&tmproto.Block{}).Marshal()
+	require.NoError(t, err)
+
+	cases := [][]byte{
+		nil,
+		{},
+		[]byte("not a proto block"),
+		emptyBlockBytes,
+	}
+	for _, data := range cases {
+		assert.NotPanics(t, func() {
+			_, _ = proof.QueryTxInclusionProof(sdk.Context{}, []string{"0"}, &abci.RequestQuery{Data: data})
+		})
+	}
+}
+
 // Ensure that we reject negative index values and avoid overflows.
 // https://github.com/celestiaorg/celestia-app/issues/3140
 func TestQueryTxInclusionProofRejectsNegativeValues(t *testing.T) {
```

### pkg/proof/querier.go
```diff
@@ -45,7 +45,7 @@ func QueryTxInclusionProof(_ sdk.Context, path []string, req *abci.RequestQuery)
 	}
 	data, err := types.DataFromProto(&pbb.Data)
 	if err != nil {
-		panic(fmt.Errorf("error from proto block: %w", err))
+		return nil, fmt.Errorf("error from proto block: %w", err)
 	}
 
 	// create and marshal the tx inclusion proof, which we return in the form of []byte
```
