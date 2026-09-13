# [?] fix(abci): fix deadlock when response callback re-enters the client (#5850)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cometbft/cometbft
Published: 2026-06-12
Source: https://github.com/cometbft/cometbft/commit/2eeb81ae552dc8348f4c892fe33020808ef049da
Type: security-commit

## Details
fix(abci): fix deadlock when response callback re-enters the client (#5850)

`resCb` and `InvokeCallback` were called while holding `cli.mtx` in both
`socketClient` and `grpcClient`. Any callback that re-enters the client
(e.g. calls `Error()` or any ABCI method) would deadlock on the same
mutex.

Snapshot `cli.resCb` under the lock, then release the lock before
invoking
both `resCb` and `reqres.InvokeCallback()`. In `grpcClient` this also
eliminates the inner `callCb` closure, moving the unlock inline for
clarity.
Add `TestResponseCallbackNoDeadlock` and
`TestGRPCResponseCallbackNoDeadlock`
to prevent regression.

To run the tests:
  go test ./abci/client/... -run TestResponseCallbackNoDeadlock -race -v
go test ./abci/client/... -run TestGRPCResponseCallbackNoDeadlock -race
-v

#### PR checklist

- [x] Tests written/updated
- [x] Changelog entry added in `CHANGELOG.md`
- [ ] Updated relevant documentation (`docs/` or `spec/`) and code
comments

---------

Co-authored-by: mergify[bot] <37929162+mergify[bot]@users.noreply.github.com>
