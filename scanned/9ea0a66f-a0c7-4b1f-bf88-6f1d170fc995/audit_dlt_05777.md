# [?] blocksync: fix flaky TestBlockPoolBasic deadlock under -race (#5867)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cometbft/cometbft
Published: 2026-06-12
Source: https://github.com/cometbft/cometbft/commit/80199cffd75512d4356d7d1e5f7792fdd18f340c
Type: security-commit

## Details
blocksync: fix flaky TestBlockPoolBasic deadlock under -race (#5867)

## Summary

Fix the CI failure at:

https://github.com/cometbft/cometbft/actions/runs/25839950951/job/75922993075

Sending to `inputChan` directly inside the `select` case blocked the
drain loop when the buffer filled up under `-race`, preventing
`requestsCh` from being drained and causing all `bpRequester` goroutines
to deadlock.

The fix replaces per-request goroutines with a single dedicated
dispatcher goroutine that is the sole consumer of `requestsCh` for the
full test lifetime. Teardown order is: `pool.Stop()` first (so the pool
stops sending to `requestsCh`), then signal the dispatcher, wait for it
to exit, then close peer channels.

## Test plan

- [x] Re-run `TestBlockPoolBasic` with `-race` to confirm no timeout

---------

Co-authored-by: Alex | Cosmos Labs <alex@cosmoslabs.io>
Co-authored-by: mergify[bot] <37929162+mergify[bot]@users.noreply.github.com>
