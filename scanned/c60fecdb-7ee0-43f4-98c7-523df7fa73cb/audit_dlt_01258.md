# [?] tests: fix panic db closed in TestDump (#16135)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2025-07-22
Source: https://github.com/erigontech/erigon/commit/1ee449d8c0b62b97963d8c6212385c4ec4aceb42
Type: security-commit

## Details
tests: fix panic db closed in TestDump (#16135)

Fixes #15427 

The root cause:
- `freezeblocks.RetireBlocksInBackground` starts a goroutine doing the
retirement of blocks in background, but there's no way to wait for
completion of such goroutine
- `TestDump` contains a loop creating a test chain at each iteration
through `MockSentry` and running a staged sync iteration over it, which
triggers the retirement of blocks (even if it's a no-op). The test
database gets closed at the end of the test by `tb.Cleanup(mock.Close)`

Hence, there's an unlikely race condition between the `TestDump`
goroutine closing the db and the background retirement goroutine
accessing the db, which may be already closed.

The changes:
- add boolean return value in `RetireBlocksInBackground` to indicate if
a new background retirement task has been scheduled or not (it may be
not if a previous one is already running)
- add `onDone` callback to signal the completion of a background
retirement task
- add `retirementStartSubscription` and `retirementDoneSubscription` in
`Events` publish-subscribe bus
- subscribe `MockSentry` to receive notifications of retirement
started/completed
- register a `testing.TB.Cleanup` hook to wait for the completion of all
the background retirements actually scheduled when
`stages2.StageLoopIteration` is called in `MockSentry` (i.e. when
`MockSentry.InsertChain` is called)
