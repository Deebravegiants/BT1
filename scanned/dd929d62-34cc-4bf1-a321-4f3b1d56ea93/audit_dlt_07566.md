# [?] core: fix data race on the BLOCKHASH cache in parallel block execution (#35441)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2026-08-04
Source: https://github.com/ethereum/go-ethereum/commit/83f0795a60437c9bd999217ed96f9e3f1e364f83
Type: security-commit

## Details
core: fix data race on the BLOCKHASH cache in parallel block execution (#35441)

## Patch
### core/state_processor_parallel.go
```diff
@@ -163,7 +163,7 @@ func (p *StateProcessor) processParallel(ctx context.Context, block *types.Block
 	// own ephemeral state instance, whose reads are served from the block-level
 	// access list overlaid on the parent state.
 	txStart := time.Now()
-	results, err := p.executeTransactionsParallel(block, parentRoot, db, base, lookup, context, signer, jumpDestCache, cfg)
+	results, err := p.executeTransactionsParallel(block, parentRoot, db, base, lookup, signer, jumpDestCache, cfg)
 	if err != nil {
 		return nil, err
 	}
@@ -249,7 +249,7 @@ func newAccessListState(db state.Database, parentRoot common.Hash, base state.Re
 // executeTransactionsParallel applies all transactions to independent,
 // access-list-backed state instances using a pool of workers, and returns
 // the per-transaction results in block order.
-func (p *StateProcessor) executeTransactionsParallel(block *types.Block, parentRoot common.Hash, db state.Database, base state.Reader, lookup *bal.Lookup, context vm.BlockContext, signer types.Signer, jumpDestCache vm.JumpDestCache, cfg vm.Config) ([]txExecResult, error) {
+func (p *StateProcessor) executeTransactionsParallel(block *types.Block, parentRoot common.Hash, db state.Database, base state.Reader, lookup *bal.Lookup, signer types.Signer, jumpDestCache vm.JumpDestCache, cfg vm.Config) ([]txExecResult, error) {
 	var (
 		config      = p.chainConfig()
 		header      = block.Header()
@@ -268,6 +268,7 @@ func (p *StateProcessor) executeTransactionsParallel(block *types.Block, parentR
 	)
 	for w := 0; w < workers; w++ {
 		group.Go(func() error {
+			context := NewEVMBlockContext(header, p.chain, nil)
 			evm := vm.NewEVM(context, nil, config, cfg)
 			if jumpDestCache != nil {
 				evm.SetJumpDestCache(jumpDestCache)
```
