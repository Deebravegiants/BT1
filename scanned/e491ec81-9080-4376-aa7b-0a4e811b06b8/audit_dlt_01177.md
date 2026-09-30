# [?] fix(test): fix race condition in BlockchainProcessorTests (flaky test) (#10513)

## Summary
Severity: Unknown
Chain: Ethereum
Component: NethermindEth/nethermind
Published: 2026-02-20
Source: https://github.com/NethermindEth/nethermind/commit/53665706d70df1a1b7e88578e3af7a8ca669ba60
Type: security-commit

## Details
fix(test): fix race condition in BlockchainProcessorTests (flaky test) (#10513)

* fix(test): fix race condition in BlockchainProcessorTests.Suggested

Wait for the BlockAdded event (not just IsKnownBlock) before returning
from Suggested(). Without this, two consecutive Suggested calls could
have their Enqueue calls interleave, causing both blocks to enter the
recovery queue in non-deterministic order and leading to a deadlock in
the test mock.

Uses a latching ManualResetEventSlim on BlockAdded rather than polling
Count, since _queueCount is transient and may drop back before being
observed when inline processing completes synchronously.

* fix: assert on wait results and handle non-best blocks

- Assert on SpinWait and blockEnqueued.Wait return values with
  descriptive timeout messages instead of silently proceeding
- Wrap BlockAdded unsubscribe in try/finally for exception safety
- Signal blockEnqueued from Task.Run finally block to handle
  non-best blocks (same/lower difficulty) where BlockAdded never
  fires because the block is not enqueued to the processor

* fix: replace ManualResetEventSlim with TaskCompletionSource

ManualResetEventSlim is disposed via `using` when Suggested() returns,
but the background Task.Run may still be blocked in SuggestBlock (due
to AllowSynchronousContinuations inline processing) and later call
Set() on the disposed object, causing ObjectDisposedException.

TaskCompletionSource has no disposal and TrySetResult is safe to call
from any thread at any time, even after the caller has moved on.

## Patch
### src/Nethermind/Nethermind.Blockchain.Test/BlockchainProcessorTests.cs
```diff
@@ -288,18 +288,62 @@ public ProcessingTestContext Suggested(Block block, BlockTreeSuggestOptions opti
             if ((options & BlockTreeSuggestOptions.ShouldProcess) != 0)
             {
                 // Use Task.Run to avoid blocking when AllowSynchronousContinuations
-                // causes inline processing on the calling thread
-                Task.Run(() =>
+                // causes inline processing on the calling thread.
+                //
+                // We wait for either BlockAdded (enqueued to processor) or SuggestBlock
+                // completion (non-best blocks that aren't enqueued) before returning. This
+                // prevents a race where two concurrent Enqueue calls both see _queueCount > 1
+                // and go to the recovery queue in non-deterministic order, causing the
+                // processor to batch blocks together and deadlock the test.
+                //
+                // TaskCompletionSource is used instead of ManualResetEventSlim because the
+                // background Task.Run may outlive this method (when AllowSynchronousContinuations
+                // causes SuggestBlock to block indefinitely) and TrySetResult is safe to call
+                // on a completed TCS without disposal concerns.
+                TaskCompletionSource suggestCompleted = new(TaskCreationOptions.RunContinuationsAsynchronously);
+                void OnBlockAdded(object? sender, BlockEventArgs args)
                 {
-                    AddBlockResult result = _blockTree.SuggestBlock(block, options);
-                    if (result != AddBlockResult.Added)
+                    if (args.Block.Hash == block.Hash)
+                        suggestCompleted.TrySetResult();
+                }
+
+                ((IBlockProcessingQueue)_processor).BlockAdded += OnBlockAdded;
+                try
+                {
+                    Task.Run(() =>
                     {
-                        _logger.Info($"Finished waiting for {block.ToString(Block.Format.Short)} as block was ignored");
-                        _resetEvent.Set();
-                    }
-                });
-                // Wait for block to be in the tree before returning
-                SpinWait.SpinUntil(() => _blockTree.IsKnownBlock(block.Number, block.Hash!), ProcessingWait);
+                        try
+                        {
+                            AddBlockResult result = _blockTree.SuggestBlock(block, options);
+                            if (result != AddBlockResult.Added)
+                            {
+                                _logger.Info($"Finished waiting for {block.ToString(Block.Format.Short)} as block was ignored");
+                                _resetEvent.Set();
+                            }
+                        }
+                        finally
+                        {
+                            // For new-best blocks, BlockAdded fires during SuggestBlock (before
+                            // this point) so the TCS is already completed. For non-best blocks
+                            // (same/lower difficulty), no enqueue occurs, so this is the signal.
+                            // When AllowSynchronousContinuations causes inline processing,
+                            // SuggestBlock blocks indefinitely but BlockAdded already fired.
+                            suggestCompleted.TrySetResult();
+                        }
+                    });
+                    Assert.That(
+                        SpinWait.SpinUntil(() => _blockTree.IsKnownBlock(block.Number, block.Hash!), ProcessingWait),
+                        Is.True,
+                        $"Timed out waiting for {block.ToString(Block.Format.Short)} to appear in the block tree");
+                    Assert.That(
+                        suggestCompleted.Task.Wait(ProcessingWait),
+                        Is.True,
+                        $"Timed out waiting for {block.ToString(Block.Format.Short)} to complete suggestion");
+                }
+                finally
+                {
+                    ((IBlockProcessingQueue)_processor).BlockAdded -= OnBlockAdded;
+                }
             }
             else
             {
```
