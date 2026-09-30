# [?] fix panic msg

## Summary
Severity: Unknown
Chain: Arbitrum
Component: OffchainLabs/nitro
Published: 2025-07-11
Source: https://github.com/OffchainLabs/nitro/commit/1a142237ff1285133ecfb873823f3558d94642de
Type: security-commit

## Details
fix panic msg

## Patch
### arbos/programs/native.go
```diff
@@ -376,7 +376,7 @@ func cacheProgram(db vm.StateDB, module common.Hash, program Program, addressFor
 			localAsm, ok = asmMap[rawdb.LocalTarget()]
 		}
 		if err != nil || !ok {
-			panic(fmt.Sprintf("failed to get compiled program for caching, program: %v, local target missing: %v, err: %v", addressForLogging.Hex(), ok, err))
+			panic(fmt.Sprintf("failed to get compiled program for caching, program: %v, local target missing: %v, err: %v", addressForLogging.Hex(), !ok, err))
 		}
 		tag := runCtx.WasmCacheTag()
 		state.CacheWasmRust(localAsm, module, program.version, tag, debug)
```
