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
