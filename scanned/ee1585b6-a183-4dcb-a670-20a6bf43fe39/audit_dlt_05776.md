# [?] fix(blocksync): fix deadlock in AddBlock caused by holding pool.mtx during sendError (#5931)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cometbft/cometbft
Published: 2026-06-16
Source: https://github.com/cometbft/cometbft/commit/87d5264799a9b30618a0dee4be5e680f070d305a
Type: security-commit

## Details
fix(blocksync): fix deadlock in AddBlock caused by holding pool.mtx during sendError (#5931)

## Summary

Fix CI failure at:
https://github.com/cometbft/cometbft/actions/runs/27214146296/job/80350996164

- `AddBlock` held `pool.mtx` via a deferred `Unlock` while calling
`sendError` on an unbuffered channel. Any concurrent caller that also
needed `pool.mtx` would deadlock until the channel was drained.
- Fix by collecting the error in `sendErr` and dispatching it inside the
`defer` after the mutex is released.
- Adds a regression test `TestAddBlockDoesNotDeadlockOnSendError`.

---

#### PR checklist

- [x] Tests written/updated
- [x] Changelog entry added in `CHANGELOG.md`
- [ ] Updated relevant documentation (`docs/` or `spec/`) and code
comments

---------

Co-authored-by: mergify[bot] <37929162+mergify[bot]@users.noreply.github.com>
