# [?] polygon/sync: ignore empty NewBlockHashes to prevent observer panic (#21560)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-06-02
Source: https://github.com/erigontech/erigon/commit/bae1c116f8e5df9bd2bfe2ef27ce3b60690a8560
Type: security-commit

## Details
polygon/sync: ignore empty NewBlockHashes to prevent observer panic (#21560)

## Summary
An **empty** NewBlockHashes packet (RLP `0xc0`) decodes to a zero-length
slice **without error**, so the surviving `execution/p2p` inbound path
delivers it to observers unpenalized. The `polygon/sync` tip-events
observer then indexed `blockHashes[0]` with no length check and
panicked; observers run in a bare `go observer(event)` with no
`recover()`, so the panic aborted the whole process — a remote,
unauthenticated **crash DoS on polygon/Bor nodes**.

Fix: ignore announcements with no entries before any `blockHashes[0]`
access.

Closes erigontech/security#72

## Scope
Only the polygon/Bor astrid path (`polygon/sync` tip-events) is affected
— it is the live consumer of inbound NewBlockHashes. On post-Merge
Ethereum the eth multi-client drops these messages (#21505), so this is
polygon-specific. `peer_tracker`'s observer ranges over the slice and is
already safe on empty; `NewBlock` decodes into a struct, so an empty
packet is rejected at decode rather than reaching an observer.

## Test plan
- [x] `TestTipEventsEmptyNewBlockHashesDoesNotPanic` — empty packet no
longer panics the observer (red→green; the red failure was `index out of
range [0] with length 0` at `tip_events.go:213`)
- [x] `TestTipEventsNewBlockHashesEmitsEvent` — non-empty announcements
still emit a `NewBlockHashes` event
- [x] `go test -race ./polygon/sync/` (new tests, `-count=5`)
- [x] `make lint` clean; `make erigon integration`

## Note
A `recover()` in `common/event` `Observers.Notify` would be
complementary defense-in-depth — it would catch any future observer
panic, not just this one — but per the issue it should not replace this
targeted length guard.

_Trimmed to 38 lines — full report: https://github.com/erigontech/erigon/commit/bae1c116f8e5df9bd2bfe2ef27ce3b60690a8560_
