# [?] cre-3269: non-determinism fix in vault gateway quorum aggregation (#21908)

## Summary
Severity: Unknown
Chain: Chainlink
Component: smartcontractkit/chainlink
Published: 2026-04-09
Source: https://github.com/smartcontractkit/chainlink/commit/fc83c52c4714d753a461403cb5be61113dafed55
Type: security-commit

## Details
cre-3269: non-determinism fix in vault gateway quorum aggregation (#21908)

## Patch
### core/services/gateway/handlers/vault/aggregator.go
```diff
@@ -5,6 +5,8 @@ import (
 	"encoding/json"
 	"errors"
 	"fmt"
+	"maps"
+	"slices"
 	"strconv"
 
 	"github.com/ethereum/go-ethereum/common"
@@ -75,8 +77,27 @@ func (a *baseAggregator) validateUsingQuorum(don capabilities.DON, resps map[str
 		if shaToCount[sha] > maxShaToCount {
 			maxShaToCount = shaToCount[sha]
 		}
-		if shaToCount[sha] >= requiredQuorum {
-			return &r, nil
+	}
+
+	var qualifiedDigests []string
+	for sha, n := range shaToCount {
+		if n >= requiredQuorum {
+			qualifiedDigests = append(qualifiedDigests, sha)
+		}
+	}
+	if len(qualifiedDigests) > 0 {
+		slices.Sort(qualifiedDigests)
+		want := qualifiedDigests[0]
+		for _, k := range slices.Sorted(maps.Keys(resps)) {
+			r := resps[k]
+			sha, err := a.sha(&r)
+			if err != nil {
+				continue
+			}
+			if sha == want {
+				out := r
+				return &out, nil
+			}
 		}
 	}
 
```

### core/services/gateway/handlers/vault/aggregator_test.go
```diff
@@ -172,6 +172,62 @@ func TestAggregator_Valid_FallsBackToQuorum_ExcludesSignaturesInSha(t *testing.T
 	assert.Contains(t, respDigests, digest)
 }
 
+func makeUnsignedVaultRPCResponse(t *testing.T, payloadJSON string) jsonrpc.Response[json.RawMessage] {
+	t.Helper()
+	sor := vaulttypes.SignedOCRResponse{
+		Payload:    json.RawMessage(payloadJSON),
+		Context:    []byte{},
+		Signatures: [][]byte{},
+	}
+	raw, err := json.Marshal(sor)
+	require.NoError(t, err)
+	rm := json.RawMessage(raw)
+	return jsonrpc.Response[json.RawMessage]{
+		Version: jsonrpc.JsonRpcVersion,
+		ID:      "quorum-tie",
+		Method:  vaulttypes.MethodSecretsCreate,
+		Result:  &rm,
+	}
+}
+
+func TestValidateUsingQuorum_tiedMajoritiesPickDigestDeterministically(t *testing.T) {
+	t.Parallel()
+
+	a := &baseAggregator{}
+	lggr := logger.Test(t)
+	don := capabilities.DON{
+		F:       1,
+		Members: make([]p2ptypes.PeerID, 6),
+	}
+
+	ra := makeUnsignedVaultRPCResponse(t, `{"v":"aaa"}`)
+	rb := makeUnsignedVaultRPCResponse(t, `{"v":"zzz"}`)
+	digestA, err := a.sha(&ra)
+	require.NoError(t, err)
+	digestB, err := a.sha(&rb)
+	require.NoError(t, err)
+	require.NotEqual(t, digestA, digestB)
+
+	wantWinner := digestA
+	if digestB < digestA {
+		wantWinner = digestB
+	}
+
+	for range 300 {
+		m := map[string]jsonrpc.Response[json.RawMessage]{
+			"n0": ra, "n1": ra, "n2": ra,
+			"n3": rb, "n4": rb, "n5": rb,
+		}
+		got, err := a.validateUsingQuorum(don, m, lggr)
+		require.NoError(t, err)
+		require.NotNil(t, got)
+		gotDigest, derr := a.sha(got)
+		require.NoError(t, derr)
+		require.Equal(t, wantWinner, gotDigest,
+			"with two disjoint 2F+1 majorities the winning digest must not depend on map iteration order")
+	}
+}
+
 func TestAggregator_InsufficientResponses(t *testing.T) {
 	mcr := &mockCapabilitiesRegistry{F: 1}
 	agg := &baseAggregator{capabilitiesRegistry: mcr}
```
