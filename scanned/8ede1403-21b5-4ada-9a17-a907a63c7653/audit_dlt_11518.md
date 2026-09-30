# [?] fix: data race in signing context GetSigners (#6967)

## Summary
Severity: Unknown
Chain: Celestia
Component: celestiaorg/celestia-app
Published: 2026-04-06
Source: https://github.com/celestiaorg/celestia-app/commit/8c4eddb6cea3452138035f315eb0b6fd0374e62b
Type: security-commit

## Details
fix: data race in signing context GetSigners (#6967)

## Summary

- Replace `cosmossdk.io/x/tx` with the celestiaorg/cosmos-sdk fork at
`x/tx/v0.13.9` which includes the fix from celestiaorg/cosmos-sdk#719
- Add a regression test (`TestSigningContextGetSignersConcurrent`) that
calls `GetSigners` concurrently and detects the race with `-race`
- Use `assert` instead of `require` in goroutines in the race test to
avoid calling `t.FailNow()` from non-test goroutines
- Add the `cosmossdk.io/x/tx` replace directive to
`test/docker-e2e/go.mod` (Go replace directives don't propagate
transitively)

## Root Cause

The upstream `cosmossdk.io/x/tx@v0.13.8` has a data race in
`signing/context.go`. The closure returned by `makeGetSignersFunc`
captures the outer function's `err` variable:

```go
func (c *Context) makeGetSignersFunc(...) (GetSignersFunc, error) {
    signersFields, err := getSignersFieldNames(descriptor)  // err declared here
    // ...
    return func(message proto.Message) ([][]byte, error) {
        var signers [][]byte
        for _, getter := range fieldGetters {
            signers, err = getter(message, signers)  // BUG: writes to captured err
        }
        return signers, nil
    }, nil
}
```

The returned function is stored in a `sync.Map` and reused by all
goroutines. When `CheckTx` (mempool recheck) and `Simulate` (gRPC gas
estimator) call it concurrently, they race on writing to the shared
`err`.

This was already fixed in the celestiaorg/cosmos-sdk fork
(celestiaorg/cosmos-sdk#719), but `cosmossdk.io/x/tx` is a separate Go
module that was pulling from the unfixed upstream v0.13.8.

## Test plan

- [x] `TestSigningContextGetSignersConcurrent` fails with `go test
-race` before the fix
- [x] `TestSigningContextGetSignersConcurrent` passes with `go test
-race` after the fix
- [x] `make build` succeeds

Closes #6966

🤖 Generated with [Claude Code](https://claude.com/claude-code)

---------

Co-authored-by: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

## Patch
### app/test/signing_race_test.go
```diff
@@ -0,0 +1,48 @@
+package app_test
+
+import (
+	"sync"
+	"testing"
+
+	"github.com/celestiaorg/celestia-app/v8/app"
+	"github.com/celestiaorg/celestia-app/v8/app/encoding"
+	"github.com/celestiaorg/celestia-app/v8/pkg/appconsts"
+	"github.com/celestiaorg/celestia-app/v8/test/util/testnode"
+	"github.com/cosmos/cosmos-sdk/codec"
+	sdk "github.com/cosmos/cosmos-sdk/types"
+	banktypes "github.com/cosmos/cosmos-sdk/x/bank/types"
+	"github.com/stretchr/testify/assert"
+)
+
+// TestSigningContextGetSignersConcurrent verifies that calling GetSigners on
+// the signing context concurrently does not trigger a data race. Before the
+// fix (adding a replace directive for cosmossdk.io/x/tx to use the patched
+// fork), the closure returned by makeGetSignersFunc captured the outer
+// function's err variable and concurrent callers would race on writing to it.
+// This test reliably fails with `go test -race` against the unfixed
+// cosmossdk.io/x/tx@v0.13.8.
+func TestSigningContextGetSignersConcurrent(t *testing.T) {
+	enc := encoding.MakeConfig(app.ModuleEncodingRegisters...)
+	cdc := enc.Codec.(*codec.ProtoCodec)
+
+	from := testnode.RandomAddress()
+	to := testnode.RandomAddress()
+	msg := &banktypes.MsgSend{
+		FromAddress: from.String(),
+		ToAddress:   to.String(),
+		Amount:      sdk.NewCoins(sdk.NewInt64Coin(appconsts.BondDenom, 10)),
+	}
+
+	const goroutines = 100
+	var wg sync.WaitGroup
+	wg.Add(goroutines)
+	for range goroutines {
+		go func() {
+			defer wg.Done()
+			signers, _, err := cdc.GetMsgV1Signers(msg)
+			assert.NoError(t, err)
+			assert.Len(t, signers, 1)
+		}()
+	}
+	wg.Wait()
+}
```

### go.mod
```diff
@@ -455,6 +455,7 @@ replace (
 	cosmossdk.io/api => github.com/celestiaorg/cosmos-sdk/api v0.7.6
 	// f48fea92e627 commit coincides with the v0.51.8 cosmos-sdk release
 	cosmossdk.io/log => github.com/celestiaorg/cosmos-sdk/log v1.1.1-0.20251116153902-f48fea92e627
+	cosmossdk.io/x/tx => github.com/celestiaorg/cosmos-sdk/x/tx v0.13.9
 	cosmossdk.io/x/upgrade => github.com/celestiaorg/cosmos-sdk/x/upgrade v0.2.0
 	github.com/cometbft/cometbft => github.com/celestiaorg/celestia-core v0.40.1
 	github.com/cosmos/cosmos-sdk => github.com/celestiaorg/cosmos-sdk v0.52.3
```

### go.sum
```diff
@@ -646,8 +646,6 @@ cosmossdk.io/x/evidence v0.1.1 h1:Ks+BLTa3uftFpElLTDp9L76t2b58htjVbSZ86aoK/E4=
 cosmossdk.io/x/evidence v0.1.1/go.mod h1:OoDsWlbtuyqS70LY51aX8FBTvguQqvFrt78qL7UzeNc=
 cosmossdk.io/x/feegrant v0.1.1 h1:EKFWOeo/pup0yF0svDisWWKAA9Zags6Zd0P3nRvVvw8=
 cosmossdk.io/x/feegrant v0.1.1/go.mod h1:2GjVVxX6G2fta8LWj7pC/ytHjryA6MHAJroBWHFNiEQ=
-cosmossdk.io/x/tx v0.13.8 h1:dQwC8jMe7awx/edi1HPPZ40AjHnsix6KSO/jbKMUYKk=
-cosmossdk.io/x/tx v0.13.8/go.mod h1:V6DImnwJMTq5qFjeGWpXNiT/fjgE4HtmclRmTqRVM3w=
 dev.gaijin.team/go/exhaustruct/v4 v4.0.0 h1:873r7aNneqoBB3IaFIzhvt2RFYTuHgmMjoKfwODoI1Y=
 dev.gaijin.team/go/exhaustruct/v4 v4.0.0/go.mod h1:aZ/k2o4Y05aMJtiux15x8iXaumE88YdiB0Ai4fXOzPI=
 dev.gaijin.team/go/golib v0.6.0 h1:v6nnznFTs4bppib/NyU1PQxobwDHwCXXl15P7DV5Zgo=
@@ -876,6 +874,8 @@ github.com/celestiaorg/cosmos-sdk/api v0.7.6 h1:81in9Zk+noz0ko+hZFSSK8L1aawFN8/C
 github.com/celestiaorg/cosmos-sdk/api v0.7.6/go.mod h1:1BgQSufu6ZQkst3YBIHDCo/TPUrhfU4fV7tOI0ftql8=
 github.com/celestiaorg/cosmos-sdk/log v1.1.1-0.20251116153902-f48fea92e627 h1:qYV81fA5E739ZtdMFCjChx0AMY+qBmMVPfRE3ol+VCE=
 github.com/celestiaorg/cosmos-sdk/log v1.1.1-0.20251116153902-f48fea92e627/go.mod h1:lQTBplaW3HQLKQdPaQq+ElW6zASAoo9r3bJ7pOr8SWo=
+github.com/celestiaorg/cosmos-sdk/x/tx v0.13.9 h1:YELTe9/1YksoqSd+Hm1uDZ6auHFNhyJrk5jvli0lbT4=
+github.com/celestiaorg/cosmos-sdk/x/tx v0.13.9/go.mod h1:V6DImnwJMTq5qFjeGWpXNiT/fjgE4HtmclRmTqRVM3w=
 github.com/celestiaorg/cosmos-sdk/x/upgrade v0.2.0 h1:GyDYfK8dLETlUI7F+w+3QYQgAszUegMXgB6cTbDm7CA=
 github.com/celestiaorg/cosmos-sdk/x/upgrade v0.2.0/go.mod h1:T4K9O18zQNKNpt4YvTL3lcUt4aKOEU05ZIFWVdQi3Ak=
 github.com/celestiaorg/go-square/v2 v2.3.3 h1:vhu6Lt39km19Q/Jk4nS3r2cuWJq6jFg+/1+iG8YGftY=
```

### test/docker-e2e/go.mod
```diff
@@ -297,6 +297,7 @@ replace (
 	cosmossdk.io/api => github.com/celestiaorg/cosmos-sdk/api v0.7.6
 	// f48fea92e627 commit coincides with the v0.51.8 cosmos-sdk release
 	cosmossdk.io/log => github.com/celestiaorg/cosmos-sdk/log v1.1.1-0.20251116153902-f48fea92e627
+	cosmossdk.io/x/tx => github.com/celestiaorg/cosmos-sdk/x/tx v0.13.9
 	cosmossdk.io/x/upgrade => github.com/celestiaorg/cosmos-sdk/x/upgrade v0.2.0
 	github.com/celestiaorg/celestia-app/v8 => ../..
 	github.com/cometbft/cometbft => github.com/celestiaorg/celestia-core v0.40.1
```

### test/docker-e2e/go.sum
```diff
@@ -634,8 +634,6 @@ cosmossdk.io/x/evidence v0.1.1 h1:Ks+BLTa3uftFpElLTDp9L76t2b58htjVbSZ86aoK/E4=
 cosmossdk.io/x/evidence v0.1.1/go.mod h1:OoDsWlbtuyqS70LY51aX8FBTvguQqvFrt78qL7UzeNc=
 cosmossdk.io/x/feegrant v0.1.1 h1:EKFWOeo/pup0yF0svDisWWKAA9Zags6Zd0P3nRvVvw8=
 cosmossdk.io/x/feegrant v0.1.1/go.mod h1:2GjVVxX6G2fta8LWj7pC/ytHjryA6MHAJroBWHFNiEQ=
-cosmossdk.io/x/tx v0.13.8 h1:dQwC8jMe7awx/edi1HPPZ40AjHnsix6KSO/jbKMUYKk=
-cosmossdk.io/x/tx v0.13.8/go.mod h1:V6DImnwJMTq5qFjeGWpXNiT/fjgE4HtmclRmTqRVM3w=
 dmitri.shuralyov.com/gpu/mtl v0.0.0-20190408044501-666a987793e9/go.mod h1:H6x//7gZCb22OMCxBHrMx7a5I7Hp++hsVxbQ4BYO7hU=
 filippo.io/edwards25519 v1.1.1 h1:YpjwWWlNmGIDyXOn8zLzqiD+9TyIlPhGFG96P39uBpw=
 filippo.io/edwards25519 v1.1.1/go.mod h1:BxyFTGdWcka3PhytdK4V28tE5sGfRvvvRV7EaN4VDT4=
@@ -788,6 +786,8 @@ github.com/celestiaorg/cosmos-sdk/api v0.7.6 h1:81in9Zk+noz0ko+hZFSSK8L1aawFN8/C
 github.com/celestiaorg/cosmos-sdk/api v0.7.6/go.mod h1:1BgQSufu6ZQkst3YBIHDCo/TPUrhfU4fV7tOI0ftql8=
 github.com/celestiaorg/cosmos-sdk/log v1.1.1-0.20251116153902-f48fea92e627 h1:qYV81fA5E739ZtdMFCjChx0AMY+qBmMVPfRE3ol+VCE=
 github.com/celestiaorg/cosmos-sdk/log v1.1.1-0.20251116153902-f48fea92e627/go.mod h1:lQTBplaW3HQLKQdPaQq+ElW6zASAoo9r3bJ7pOr8SWo=
+github.com/celestiaorg/cosmos-sdk/x/tx v0.13.9 h1:YELTe9/1YksoqSd+Hm1uDZ6auHFNhyJrk5jvli0lbT4=
+github.com/celestiaorg/cosmos-sdk/x/tx v0.13.9/go.mod h1:V6DImnwJMTq5qFjeGWpXNiT/fjgE4HtmclRmTqRVM3w=
 github.com/celestiaorg/cosmos-sdk/x/upgrade v0.2.0 h1:GyDYfK8dLETlUI7F+w+3QYQgAszUegMXgB6cTbDm7CA=
 github.com/celestiaorg/cosmos-sdk/x/upgrade v0.2.0/go.mod h1:T4K9O18zQNKNpt4YvTL3lcUt4aKOEU05ZIFWVdQi3Ak=
 github.com/celestiaorg/go-square/v2 v2.3.3 h1:vhu6Lt39km19Q/Jk4nS3r2cuWJq6jFg+/1+iG8YGftY=
```
