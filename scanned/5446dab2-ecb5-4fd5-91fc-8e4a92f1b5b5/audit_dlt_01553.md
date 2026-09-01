# [?] fix: re-enable test_scheduler_drop_idle by resolving race condition (#9042)

## Summary
Severity: Unknown
Chain: Solana
Component: anza-xyz/agave
Published: 2025-11-19
Source: https://github.com/anza-xyz/agave/commit/35f53334b125ad61a527ae58d9bd46a1aa91d1f1
Type: security-commit

## Details
fix: re-enable test_scheduler_drop_idle by resolving race condition (#9042)

* fix: re-enable test_scheduler_drop_idle by resolving race condition

  Remove #[ignore] attribute and fix timing to eliminate race condition
  in test_scheduler_drop_idle, which was disabled in PR #8278.

  The test verifies the scheduler pool's cleaner thread correctly removes
  idle schedulers while preserving recently-pooled ones.

  Root cause:
  The original test used a 100ms idle threshold with 1000ms sleep, but
  timing was still unreliable due to system variations. The race occurred
  when old_scheduler and new_scheduler had unclear age differences.

  Fix:
  - Use explicit 300ms idle threshold for this test (instead of 100ms)
  - Sleep 350ms before returning new_scheduler (provides 50ms+ safety margin)
  - This guarantees old_scheduler is idle while new_scheduler is not

  Result:
  - old_scheduler: 350ms old (> 300ms threshold) → definitely idle → removed
  - new_scheduler: ~0ms old (< 300ms threshold) → definitely not idle → kept
  - Test is now deterministic and matches expected checkpoint sequence

  Fixes #8279

Signed-off-by: AvhiMaz <avhimazumder5@outlook.com>

* Address all reviewer feedback on test_scheduler_drop_idle

   - Move SHORTENED_MAX_POOLING_DURATION constant to test_scheduler_drop_stale where it's used
   - Convert test_max_pooling_duration from let to const TEST_MAX_POOLING_DURATION following conventions
   - Create TEST_WAIT_FOR_IDLE constant (500ms) with explicit safety margin tied to TEST_MAX_POOLING_DURATION
   - Increase safety margin from 50ms to 200ms for CI reliability
   - Add detailed comments explaining 300ms pooling duration tradeoff (speed vs race condition window)
   - Update assertion comment with explicit timing guarantees: old_scheduler ~500ms old (exceeds 300ms threshold),
   new_scheduler ~50ms old (below threshold)

_Trimmed to 38 lines — full report: https://github.com/anza-xyz/agave/commit/35f53334b125ad61a527ae58d9bd46a1aa91d1f1_
