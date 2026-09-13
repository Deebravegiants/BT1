# [?] Fix flaky tests: timing and race condition (#10455)

## Summary
Severity: Unknown
Chain: Ethereum
Component: NethermindEth/nethermind
Published: 2026-02-08
Source: https://github.com/NethermindEth/nethermind/commit/129fcbfe72e7affdbb7734e66fcd8abcb9975413
Type: security-commit

## Details
Fix flaky tests: timing and race condition (#10455)

- PeerManagerTests: Increase After timeout from 1000ms to 3000ms in
  Will_not_stop_trying_on_rlpx_connection_failure to prevent false
  failures on loaded CI runners
- SyncServerTests: Use Interlocked.Increment in
  Broadcast_NewBlock_on_arrival_to_sqrt_of_peers to fix race condition
  where concurrent SyncPeerMock background threads could lose count
  increments
- Rename _travisDelay fields to _delay, _delayLong, _delayLonger

Co-authored-by: Claude Opus 4.6 <noreply@anthropic.com>
