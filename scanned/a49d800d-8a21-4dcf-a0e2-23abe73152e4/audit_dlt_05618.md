# [?] rpc: fix non-deterministic eth_estimateGas caused by stale cancel of shared EVM (#22877)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-08-02
Source: https://github.com/erigontech/erigon/commit/e540242509a0b497eb7d244fc5b26bc0fd6e8934
Type: security-commit

## Details
rpc: fix non-deterministic eth_estimateGas caused by stale cancel of shared EVM (#22877)

Fixes #22870.

`eth_estimateGas` intermittently returns a gas limit below the smallest
one at which the call succeeds, so using the estimate makes the
transaction revert out of gas.

In `ReusableCaller.DoCallWithNewGas` the per-probe watcher goroutine
races the deferred `cancel()` against the `done` channel: on normal
return both select cases are ready, so ~half the time it calls
`evm.Cancel()` on the shared EVM after its own probe has finished. If
that goroutine runs after the next probe's `evm.Reset()`, the next
probe's frame-entry check in `evm.call` consumes the abort and returns
`err == nil`, so a gas limit that should have failed is classified as
success and the binary search converges below the true minimum.

Fix: replace the goroutine with `context.AfterFunc` + deferred `stop()`
(same shape as `setupEVMTimeout` in `eth_callMany.go`). `stop()` is
deferred after `cancel()`, so it runs first and the callback cannot fire
on normal return; a genuine timeout still cancels mid-execution and
returns the timeout error as before.

`TestEstimateGasDeterminism` reproduces it: 200 identical serial
requests at a fixed head returned 20 distinct (all-low) values before
the fix, and are deterministic after. `go test ./...` and `make lint`
pass.

---------

Co-authored-by: lupin012 <58134934+lupin012@users.noreply.github.com>
