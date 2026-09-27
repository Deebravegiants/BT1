# [?] fix(istanbul): break Start/NewChainHead deadlock on coreMu

## Summary
Severity: Unknown
Chain: Kaia
Component: kaiachain/kaia
Published: 2026-06-17
Source: https://github.com/kaiachain/kaia/commit/e165330daaa8c29a45a486c46c0a90c6955a3d9a
Type: security-commit

## Details
fix(istanbul): break Start/NewChainHead deadlock on coreMu

backend.Start holds coreMu while core.Start synchronously posts a
NewSequenceEvent to the worker's event loop and waits for it to be consumed.
That same loop, when handling a ChainHeadEvent, calls backend.NewChainHead,
which took coreMu.RLock. When a node finishes syncing and resumes mining (the
sync->mine transition, with a freshly imported block's ChainHeadEvent still in
flight) the two collide: Start holds the write lock and waits for the worker,
while the worker is blocked acquiring the read lock -> permanent deadlock. All
later consensus message handling (HandleMsg) and even shutdown (Stop, which also
locks coreMu) then block, so the node freezes and can only be SIGKILLed.

NewChainHead only needs coreMu to read the coreStarted flag before an
already-asynchronous event post. Make coreStarted an atomic.Bool and read it
locklessly in NewChainHead so the worker loop never blocks on coreMu;
Start/Stop/HandleMsg keep their existing coreMu usage. This removes the
lock-vs-channel cycle without changing any consensus event timing. Pre-existing
issue (not permissionless-specific); it surfaced once nodes could actually catch
up via sync and reach the sync->mine transition.

Constraint: NewChainHead runs in the worker event loop and must never block on coreMu
Rejected: make the NewSequenceEvent post async | changes consensus event ordering
Rejected: drop coreMu across core.Start in backend.Start | widens the Start/Stop lifecycle race window
Confidence: high
Scope-risk: narrow
Directive: do not reintroduce coreMu (or any lock backend.Start holds) into NewChainHead
Not-tested: snap/fast-sync paths (reproduced and verified on the full-sync sync->mine transition)

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
