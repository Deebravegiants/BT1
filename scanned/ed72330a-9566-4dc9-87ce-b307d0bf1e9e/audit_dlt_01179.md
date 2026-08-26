# [?] Fix BackgroundTaskScheduler queue overflow during block processing (#10488)

## Summary
Severity: Unknown
Chain: Ethereum
Component: NethermindEth/nethermind
Published: 2026-02-12
Source: https://github.com/NethermindEth/nethermind/commit/bd3af149a27893beacf588529d2e89eaa150761e
Type: security-commit

## Details
Fix BackgroundTaskScheduler queue overflow during block processing (#10488)

* Initial plan

* Fix BackgroundTaskScheduler queue overflow by removing signal wait from scheduler threads

During block processing, ManualResetEventSlim blocked all scheduler threads
in BelowNormalPriorityTaskScheduler, preventing StartChannel from draining
expired tasks. New tasks (P2P transaction messages) continued arriving,
filling the queue beyond capacity (1024) and triggering task drops.

Fix: Remove the ManualResetEventSlim signal entirely. The existing
cancellation token mechanism in StartChannel already handles block
processing correctly — expired tasks get drained with cancelled tokens
(fast return), while non-expired tasks are re-queued with a 1ms throttle
until their deadline passes or block processing ends.

Co-authored-by: kamilchodola <43241881+kamilchodola@users.noreply.github.com>

* Replace blocking ManualResetEventSlim with async TaskCompletionSource signal; add high-capacity stress test

The original ManualResetEventSlim blocked scheduler threads in
ProcessBackgroundTasks(), preventing StartChannel from draining expired
tasks during block processing. Replace with TaskCompletionSource-based
async signal awaited in StartChannel's Throttle path.

Add comprehensive stress test that fills a 1024-capacity queue across
multiple block processing cycles, verifying:
- Tasks are dropped when queue exceeds capacity
- Expired tasks drain with cancelled tokens during block processing
- Queue recovers and accepts new tasks after draining
- Mixed short/long-lived tasks behave correctly across cycles
- Queue remains fully operational after repeated block processing

Co-authored-by: kamilchodola <43241881+kamilchodola@users.noreply.github.com>

* Double BackgroundTaskMaxNumber default from 1024 to 2048


_Trimmed to 38 lines — full report: https://github.com/NethermindEth/nethermind/commit/bd3af149a27893beacf588529d2e89eaa150761e_
