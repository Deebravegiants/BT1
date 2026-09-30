# [?] cre-3262: non-determinism fix in confidential relay aggregator (#21907)

## Summary
Severity: Unknown
Chain: Chainlink
Component: smartcontractkit/chainlink
Published: 2026-04-08
Source: https://github.com/smartcontractkit/chainlink/commit/c51df77cec377dd887748f97d16b5d1f16db9681
Type: security-commit

## Details
cre-3262: non-determinism fix in confidential relay aggregator (#21907)

## Patch
### core/services/gateway/handlers/confidentialrelay/aggregator.go
```diff
@@ -4,6 +4,8 @@ import (
 	"encoding/json"
 	"errors"
 	"fmt"
+	"maps"
+	"slices"
 
 	jsonrpc "github.com/smartcontractkit/chainlink-common/pkg/jsonrpc2"
 	"github.com/smartcontractkit/chainlink-common/pkg/logger"
@@ -41,8 +43,27 @@ func (a *aggregator) Aggregate(resps map[string]jsonrpc.Response[json.RawMessage
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
+			sha, err := r.Digest()
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

### core/services/gateway/handlers/confidentialrelay/aggregator_test.go
```diff
@@ -0,0 +1,63 @@
+package confidentialrelay
+
+import (
+	"encoding/json"
+	"testing"
+
+	"github.com/stretchr/testify/require"
+
+	jsonrpc "github.com/smartcontractkit/chainlink-common/pkg/jsonrpc2"
+	"github.com/smartcontractkit/chainlink-common/pkg/logger"
+)
+
+func TestAggregator_tiedMajoritiesPickDigestDeterministically(t *testing.T) {
+	t.Parallel()
+
+	lggr := logger.Test(t)
+	agg := &aggregator{}
+
+	const id = "req-tie"
+	makeResp := func(payload string) jsonrpc.Response[json.RawMessage] {
+		buf, err := json.Marshal(map[string]string{"payload": payload})
+		require.NoError(t, err)
+		rd := make(json.RawMessage, len(buf))
+		copy(rd, buf)
+		return jsonrpc.Response[json.RawMessage]{
+			Version: jsonrpc.JsonRpcVersion,
+			ID:      id,
+			Method:  MethodCapabilityExec,
+			Result:  &rd,
+		}
+	}
+
+	a := makeResp("aaa")
+	b := makeResp("zzz")
+	digestA, err := a.Digest()
+	require.NoError(t, err)
+	digestB, err := b.Digest()
+	require.NoError(t, err)
+	require.NotEqual(t, digestA, digestB, "fixtures must produce distinct digests")
+
+	wantWinnerDigest := digestA
+	if digestB < digestA {
+		wantWinnerDigest = digestB
+	}
+
+	// Two nodes report A, two report B: each side has F+1 when F=1. Map iteration order
+	// must not change which digest wins.
+	for range 300 {
+		m := map[string]jsonrpc.Response[json.RawMessage]{
+			"n0": a,
+			"n1": a,
+			"n2": b,
+			"n3": b,
+		}
+		got, err := agg.Aggregate(m, 1, 4, lggr)
+		require.NoError(t, err)
+		require.NotNil(t, got)
+		gotDigest, derr := got.Digest()
+		require.NoError(t, derr)
+		require.Equal(t, wantWinnerDigest, gotDigest,
+			"with tied majorities the chosen digest must be order-independent (lexicographically smallest qualifying digest)")
+	}
+}
```
