# [?] fix: BackgroundTaskScheduler disposal deadlock causing CI timeouts (#10927)

## Summary
Severity: Unknown
Chain: Ethereum
Component: NethermindEth/nethermind
Published: 2026-03-23
Source: https://github.com/NethermindEth/nethermind/commit/82ab1a7e5d75a37f60b60f5523a567485b365ab2
Type: security-commit

## Details
fix: BackgroundTaskScheduler disposal deadlock causing CI timeouts (#10927)

* fix: resolve BackgroundTaskScheduler disposal deadlock causing CI timeouts

The scheduler worker threads exited on cancellation before StartChannel()
continuations could complete, causing Task.WhenAll to wait forever.

- Remove CancellationToken from BelowNormalPriorityTaskScheduler workers
  so they stay alive until CompleteAdding() is called via Dispose()
- Wrap StartChannel() outer loop with OperationCanceledException catch
  so WaitToReadAsync cancellation completes the task cleanly
- Workers now exit naturally after executor tasks finish, not before

* fix: address PR feedback - TryWrite guard, OCE filter, test timeout

- Only increment _queueCount if TryWrite succeeds; if re-queue fails
  (channel completed during dispose), fall through to run with cancelled
  token instead of skewing the counter
- Filter inner OCE catch with `when (cts.IsCancellationRequested)` to
  avoid swallowing unexpected cancellations from activity handlers
- Increase test timeout from 2s to 5s with assertion message for CI

* fix: Assert.DoesNotThrowAsync returns void, not Task - remove await
