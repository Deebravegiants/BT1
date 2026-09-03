# [?] fix(mempool): Fix data race when rechecking with async ABCI client (#2268)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cometbft/cometbft
Published: 2024-05-07
Source: https://github.com/cometbft/cometbft/commit/f3775f4bbfd1528b21f13660f2a76ddb3255101f
Type: security-commit

## Details
fix(mempool): Fix data race when rechecking with async ABCI client (#2268)

Fixes ~~#2225 and~~ #1827 

(#2225 is now fixed in a separate PR, #2894)

The bug: during rechecking, when the `CheckTxAsync` request for the last
transaction fails, then the `resCbRecheck` callback on the response is
not called, and the recheck variables end up in a wrong state
(`recheckCursor != nil`, meaning that recheck has not finished). This
will cause a panic next time a new transaction arrives, and the
`CheckTx` response finds that rechecking hasn't finished.

This problem only happens when using the non-local ABCI client, where
`CheckTx` responses may arrive late or never, so the response won't be
processed by the callback. We have two options to fix this.
1. When we call `CheckTxAsync`, block waiting for a response. If the
response never arrives, it will block `Update` forever.
2. After sending all recheck requests, we flush the app connection and
set a timer to wait for late recheck responses. After the timer expires,
we finalise rechecking properly. If a CheckTx response arrives late, we
consider that it is safe to ignore it.

This PR implements option 2, as we cannot allow the risk to block the
node forever waiting for a response.

With the proposed changes, now when we reach the end of the rechecking
process, all requests and responses will be processed or discared, and
`recheckCursor` will always be `nil`.

This PR also:
- refactors all recheck logic to put it into a separate `recheck`
struct. The fix to the bug described above is the only change in the
recheck logic.
- adds 4 new tests.

---


_Trimmed to 38 lines — full report: https://github.com/cometbft/cometbft/commit/f3775f4bbfd1528b21f13660f2a76ddb3255101f_
