# [?] fix(genesis): panic when build genesis

## Summary
Severity: Unknown
Chain: VeChain
Component: vechain/thor
Published: 2018-05-29
Source: https://github.com/vechain/thor/commit/64b2eab7c4a9df56c97e49ada5da013674a44b0d
Type: security-commit

## Details
fix(genesis): panic when build genesis

## Patch
### genesis/builder.go
```diff
@@ -10,6 +10,7 @@ import (
 
 	"github.com/pkg/errors"
 	"github.com/vechain/thor/block"
+	"github.com/vechain/thor/builtin"
 	"github.com/vechain/thor/lvldb"
 	"github.com/vechain/thor/runtime"
 	"github.com/vechain/thor/state"
@@ -84,7 +85,9 @@ func (b *Builder) Build(stateCreator *state.Creator) (blk *block.Block, events t
 	rt := runtime.New(nil, state, thor.Address{}, 0, b.timestamp, b.gasLimit)
 
 	for _, call := range b.calls {
-		out := rt.Call(call.clause, 0, math.MaxUint64, nil)
+		out := rt.Call(call.clause, 0, math.MaxUint64, &builtin.TransactionEnv{
+			Origin: call.caller,
+		})
 		if out.VMErr != nil {
 			return nil, nil, errors.Wrap(out.VMErr, "vm")
 		}
```
