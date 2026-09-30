# [?] Fix onStoreLog() crash

## Summary
Severity: Unknown
Chain: Polygon zkEVM
Component: 0xPolygon/zkevm-prover
Published: 2023-03-31
Source: https://github.com/0xPolygon/zkevm-prover/commit/67b680cae7df1edf130e8c14e1bd60d93488f981
Type: security-commit

## Details
Fix onStoreLog() crash

## Patch
### src/main_sm/fork_4/main/full_tracer.cpp
```diff
@@ -1327,7 +1327,7 @@ zkresult FullTracer::onOpcode(Context &ctx, const RomCommand &cmd)
         singleInfo.memory_size = (auxScalar.get_ui() / 32) * 32;
     }
 
-    if (ctx.proverRequest.input.traceConfig.bGenerateStorage && increaseDepth)
+    if (ctx.proverRequest.input.traceConfig.bGenerateStorage /*&& increaseDepth*/)
     {
         unordered_map<string, string> auxMap;
         deltaStorage[depth + 1] = auxMap;
```
