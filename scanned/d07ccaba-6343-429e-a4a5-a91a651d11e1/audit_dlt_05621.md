# [?] execution: fix GetAssembledBlock deadlock (#22835)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-07-29
Source: https://github.com/erigontech/erigon/commit/8cc9d5271800307d7386450acc5b1b745144459a
Type: security-commit

## Details
execution: fix GetAssembledBlock deadlock (#22835)

fixes https://github.com/erigontech/erigon/issues/22631

## Summary

- Make `BlockBuilder.Stop` wait for either builder completion or
cancellation of the caller's context.
- Propagate the `GetAssembledBlock` request context into the builder
wait.
- Add a regression test using the real txpool with `lastSeenBlock`
behind the builder's parent.

## Root cause

During a rapid reorg, an asynchronous payload builder could remain based
on block N after the txpool had unwound to N-1. The builder then waited
in `TxPool.best` for the txpool to reach N.

When the consensus client subsequently requested that payload,
`GetAssembledBlock` ignored request cancellation and waited indefinitely
in `BlockBuilder.Stop`. This retained the execution semaphore and the
Engine API's outer lock, preventing later `newPayload` and
`forkchoiceUpdated` requests from advancing execution and notifying the
txpool. The resulting circular wait could wedge stateful Engine API
traffic indefinitely.

## Change

Replace the builder's completion condition variable with a completion
channel while continuing to protect its result with a mutex.
`BlockBuilder.Stop` now selects between that completion channel and
`ctx.Done()`.

When a payload request is canceled or reaches its deadline,
`GetAssembledBlock` returns the context error and releases the execution
semaphore. This allows the Engine API handler to unwind and newer
stateful requests to proceed. Normal completed-builder behavior remains

_Trimmed to 38 lines — full report: https://github.com/erigontech/erigon/commit/8cc9d5271800307d7386450acc5b1b745144459a_
