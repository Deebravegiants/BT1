# [?] Add patch for eth bug GHSA-9856-9gg9-qcmq (#3856)

## Summary
Severity: Unknown
Chain: Harmony
Component: harmony-one/harmony
Published: 2021-08-27
Source: https://github.com/harmony-one/harmony/commit/f741ca81c2d12406d4a218d86f0038e7d2892dc1
Type: security-commit

## Details
Add patch for eth bug GHSA-9856-9gg9-qcmq (#3856)

## Patch
### core/vm/instructions.go
```diff
@@ -767,6 +767,7 @@ func opCall(pc *uint64, interpreter *EVMInterpreter, contract *Contract, memory
 		stack.push(interpreter.intPool.get().SetUint64(1))
 	}
 	if err == nil || err == ErrExecutionReverted {
+		ret = common.CopyBytes(ret)
 		memory.Set(retOffset.Uint64(), retSize.Uint64(), ret)
 	}
 	contract.Gas += returnGas
@@ -796,6 +797,7 @@ func opCallCode(pc *uint64, interpreter *EVMInterpreter, contract *Contract, mem
 		stack.push(interpreter.intPool.get().SetUint64(1))
 	}
 	if err == nil || err == ErrExecutionReverted {
+		ret = common.CopyBytes(ret)
 		memory.Set(retOffset.Uint64(), retSize.Uint64(), ret)
 	}
 	contract.Gas += returnGas
@@ -821,6 +823,7 @@ func opDelegateCall(pc *uint64, interpreter *EVMInterpreter, contract *Contract,
 		stack.push(interpreter.intPool.get().SetUint64(1))
 	}
 	if err == nil || err == ErrExecutionReverted {
+		ret = common.CopyBytes(ret)
 		memory.Set(retOffset.Uint64(), retSize.Uint64(), ret)
 	}
 	contract.Gas += returnGas
@@ -846,6 +849,7 @@ func opStaticCall(pc *uint64, interpreter *EVMInterpreter, contract *Contract, m
 		stack.push(interpreter.intPool.get().SetUint64(1))
 	}
 	if err == nil || err == ErrExecutionReverted {
+		ret = common.CopyBytes(ret)
 		memory.Set(retOffset.Uint64(), retSize.Uint64(), ret)
 	}
 	contract.Gas += returnGas
```
