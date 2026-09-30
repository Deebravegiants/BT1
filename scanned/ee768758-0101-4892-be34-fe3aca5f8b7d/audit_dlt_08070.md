# [?] eth: fix tracer panic when running without configs + reexec (#15799)

## Summary
Severity: Unknown
Chain: Celo
Component: celo-org/celo-blockchain
Published: 2018-01-04
Source: https://github.com/celo-org/celo-blockchain/commit/ae71da1b03c6eee82b714ef81b4fc59bcc130bb2
Type: security-commit

## Details
eth: fix tracer panic when running without configs + reexec (#15799)

## Patch
### eth/api_tracer.go
```diff
@@ -204,7 +204,7 @@ func (api *PrivateDebugAPI) traceChain(ctx context.Context, start, end *types.Bl
 	if err != nil {
 		// If the starting state is missing, allow some number of blocks to be reexecuted
 		reexec := defaultTraceReexec
-		if config.Reexec != nil {
+		if config != nil && config.Reexec != nil {
 			reexec = *config.Reexec
 		}
 		// Find the most recent block that has the state available
@@ -465,7 +465,7 @@ func (api *PrivateDebugAPI) traceBlock(ctx context.Context, block *types.Block,
 		return nil, fmt.Errorf("parent %x not found", block.ParentHash())
 	}
 	reexec := defaultTraceReexec
-	if config.Reexec != nil {
+	if config != nil && config.Reexec != nil {
 		reexec = *config.Reexec
 	}
 	statedb, err := api.computeStateDB(parent, reexec)
@@ -619,7 +619,7 @@ func (api *PrivateDebugAPI) TraceTransaction(ctx context.Context, hash common.Ha
 		return nil, fmt.Errorf("transaction %x not found", hash)
 	}
 	reexec := defaultTraceReexec
-	if config.Reexec != nil {
+	if config != nil && config.Reexec != nil {
 		reexec = *config.Reexec
 	}
 	msg, vmctx, statedb, err := api.computeTxEnv(blockHash, int(index), reexec)
```
