# [?] fix(rpc): reject negative genesis_chunked index instead of panicking (#6070)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cometbft/cometbft
Published: 2026-09-21
Source: https://github.com/cometbft/cometbft/commit/9f41e825b75033f5a143a4b7744eb8abab13369c
Type: security-commit

## Details
fix(rpc): reject negative genesis_chunked index instead of panicking (#6070)

## Problem

`/genesis_chunked?chunk=N` takes `N` as `uint`, casts it to `int` and
only checks the upper bound. For `N >= 2^63` the cast goes negative, the
check passes, and `env.genChunks[id]` panics:

```
$ curl 'http://127.0.0.1:26657/genesis_chunked?chunk=18446744073709551615'
... panic: runtime error: index out of range [-1]
```

The handler recovers it, but that is one unauthenticated request per
stack trace in the node's log. Same family as the id parsing issue fixed
in #5861.

## Change

- reject `id < 0` in the same branch as the too-large check
- unit test with a valid index plus `2`, `math.MaxUint`, `1<<63`

## Checklist

- [x] tests
- [x] changelog
- [ ] docs (n/a)

## Patch
### CHANGELOG.md
```diff
@@ -8,6 +8,8 @@
 
 ### BUG FIXES
 
+- `[rpc]` reject out-of-range `/genesis_chunked` indices that wrap to a negative int instead of panicking
+  ([\#6070](https://github.com/cometbft/cometbft/pull/6070))
 - `[lp2p]` fix flaky MsgBytesFilter test by avoiding broadcast race
   ([\#6053](https://github.com/cometbft/cometbft/pull/6053))
 - `[spec]` fix the inductive invariant `spec/light-client/accountability`
```

### rpc/core/net.go
```diff
@@ -117,9 +117,11 @@ func (env *Environment) GenesisChunked(_ *rpctypes.Context, chunk uint) (*ctypes
 		return nil, fmt.Errorf("service configuration error, there are no chunks")
 	}
 
+	// chunk is client-controlled; values >= 2^63 wrap to a negative int and
+	// must be rejected like any other out-of-range index.
 	id := int(chunk)
 
-	if id > len(env.genChunks)-1 {
+	if id < 0 || id > len(env.genChunks)-1 {
 		return nil, fmt.Errorf("there are %d chunks, %d is invalid", len(env.genChunks)-1, id)
 	}
 
```

### rpc/core/net_test.go
```diff
@@ -1,6 +1,7 @@
 package core
 
 import (
+	"math"
 	"testing"
 
 	"github.com/stretchr/testify/assert"
@@ -87,3 +88,17 @@ func TestUnsafeDialPeers(t *testing.T) {
 		}
 	}
 }
+
+func TestGenesisChunkedRejectsOutOfRangeIndex(t *testing.T) {
+	env := &Environment{genChunks: []string{"a", "b"}}
+
+	res, err := env.GenesisChunked(&rpctypes.Context{}, 1)
+	require.NoError(t, err)
+	assert.Equal(t, "b", res.Data)
+
+	for _, chunk := range []uint{2, math.MaxUint, 1 << 63} {
+		res, err := env.GenesisChunked(&rpctypes.Context{}, chunk)
+		require.Error(t, err, "chunk %d", chunk)
+		assert.Nil(t, res)
+	}
+}
```
