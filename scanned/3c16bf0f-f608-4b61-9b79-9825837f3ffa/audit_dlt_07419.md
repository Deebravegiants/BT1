# [?] fix: resolve flaky p2p_client test race condition on ARM64 (#21088)

## Summary
Severity: Unknown
Chain: Aztec
Component: AztecProtocol/aztec-packages
Published: 2026-03-04
Source: https://github.com/AztecProtocol/aztec-packages/commit/695e8fbc8088a48be26bdf8d63378b3f67933101
Type: security-commit

## Details
fix: resolve flaky p2p_client test race condition on ARM64 (#21088)

Fixes a flaky test failure that dequeued
https://github.com/AztecProtocol/aztec-packages/pull/21084 from the
merge queue.

The test `triggers tx collection for missing txs from mined blocks` in
`p2p_client.test.ts` was flaky because `client.start()` kicks off a
background block stream that processes the initial 100 blocks. This
background work could complete before the test overrides the `hasTxs`
mock, so `startCollecting` gets called for block 100 with the default
mock (making all txs look "missing").

**Fix**: Drain the initial background sync with an explicit `sync()`
call before setting up the test scenario, and clear stale mock calls
with `mockClear()` before the assertion sync.

ClaudeBox log: http://ci.aztec-labs.com/5c9e693e161264ba-1

## Patch
### yarn-project/p2p/src/client/p2p_client.test.ts
```diff
@@ -381,12 +381,17 @@ describe('P2P Client', () => {
 
     it('triggers tx collection for missing txs from mined blocks', async () => {
       await client.start();
+      // Drain any initial background sync that processes the initial blocks (1-100),
+      // which may call startCollecting depending on timing.
+      await client.sync();
+
       const block = await L2Block.random(BlockNumber(101), { txsPerBlock: 3 });
       // Compute the block hash since it gets cached when the p2p client logs it
       await block.hash();
 
       txPool.hasTxs.mockResolvedValue([true, false, true]);
       blockSource.addProposedBlocks([block]);
+      txCollection.startCollecting.mockClear();
       await client.sync();
 
       expect(txCollection.startCollecting).toHaveBeenCalledTimes(1);
```
