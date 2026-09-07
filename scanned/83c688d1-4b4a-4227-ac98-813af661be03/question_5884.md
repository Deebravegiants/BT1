# Q5884: Watcher give-up Aleo via PoaBridge

## Question
For Aleo via PoaBridge, `getWithdrawalStatsForChain` derives a hard timeout (3x p99) after which `watchWithdrawal` throws `WithdrawalWatchError`, and `MAX_CONSECUTIVE_ERRORS = 5` transient failures also throw. Can an unprivileged user pick a destination/time such that the bridge completes after the SDK gave up, so an integrator that treats `WithdrawalWatchError` as failure refunds the user while the bridge also delivers, paying twice?

## Target
- File/function: packages/intents-sdk/src/core/withdrawal-watcher.ts `watchWithdrawal`; packages/intents-sdk/src/constants/withdrawal-timing.ts `getWithdrawalStatsForChain`
- Entrypoint: `IntentsSDK.waitForWithdrawalCompletion` / `processWithdrawal`
- Attacker controls: destination chain choice, batch size (HOT sequential waits), time of submission
- Exploit idea: Timeout is a fixed multiple of historical p99; the error type does not distinguish 'unknown' from 'failed'. `processWithdrawal` surfaces it as a thrown error.
- Invariant to test: the SDK never returns/throws a terminal 'failed' signal for a withdrawal that can still complete; unknown must be distinguishable from failed.
- Expected Immunefi impact: High - status/hash misreport making an integrator credit or refund twice (HackenProof: withdrawal processing / serialization correctness)
- Fast validation: vitest with fake timers: mock describeWithdrawal pending past p99 then completed; assert error type and document integrator guidance.
