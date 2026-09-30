# [?] caplin: fix BlockCollector crash-loop on gap in collected blocks (#20130)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-03-24
Source: https://github.com/erigontech/erigon/commit/26e6f5bdb49ae6f341597bed96377aaa4cc1ee3f
Type: security-commit

## Details
caplin: fix BlockCollector crash-loop on gap in collected blocks (#20130)

## Summary

Cherry-pick of #20125 from `release/3.4` to `main`.

- Replace `panic` with `warn + break` in
`PersistentBlockCollector.Flush()` when a gap is detected in collected
block numbers
- The persistent MDBX DB can accumulate non-contiguous blocks across
process restarts; panicking prevents the DB from ever being cleared,
causing a permanent crash-loop
- Now inserts the contiguous prefix of blocks, logs a warning, clears
the DB, and lets the next sync cycle re-download the missing range

Fixes https://github.com/erigontech/erigon-qa/issues/383

## Test plan

- [ ] Verify `make lint && make erigon` passes
- [ ] Run Chiado sync and confirm no panic on block gap
- [ ] Confirm gap warning is logged and sync self-heals

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-authored-by: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

## Patch
### cl/phase1/execution_client/block_collector/persistent_block_collector.go
```diff
@@ -163,7 +163,10 @@ func (p *PersistentBlockCollector) Flush(ctx context.Context) error {
 			}
 
 			if prevBlockNum > 0 && block.NumberU64() != prevBlockNum+1 {
-				panic(fmt.Sprintf("assert: BlockCollector inserting gap: %d -> %d. To fix try: `rm datadir/caplin/history datadir/chaindata`", prevBlockNum, block.NumberU64()))
+				p.logger.Warn("[BlockCollector] Gap detected in collected blocks, will re-download missing range",
+					"lastBlock", prevBlockNum, "nextBlock", block.NumberU64(),
+					"gap", block.NumberU64()-prevBlockNum-1)
+				break
 			}
 			prevBlockNum = block.NumberU64()
 			blocksBatch = append(blocksBatch, block)
```
