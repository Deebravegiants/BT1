# [?] fix(coinjoin): make pending-observation locks crash-safe and cheap to poll

## Summary
Severity: Unknown
Chain: Dash
Component: dashpay/dash
Published: 2026-07-25
Source: https://github.com/dashpay/dash/commit/f9c4bebea16e4a91a45bbda63917c0da78e9ec77
Type: security-commit

## Details
fix(coinjoin): make pending-observation locks crash-safe and cheap to poll

Review follow-ups to the pending-observation mechanism:

- AddPendingObservation() persisted the wallet locks before the
  cj_pending_obs record which owns them. Those are two separate writes, so
  a crash in between left persistently locked coins behind with nothing
  tracking them and no timeout to release them. Write the record first and
  only persist the locks if that succeeded; the resulting order is
  self-healing, CheckPendingObservations() drops a pending entry as soon as
  it sees its coin is not locked.

- CheckPendingObservations() constructed a WalletBatch on every pass, and
  every WalletBatch checkpoints the wallet database when it goes out of
  scope. Open it lazily, on the first actual write, and read the record
  with fFlushOnClose=false.

- Do not persist the timer refresh applied to an input which is spent in
  chain/mempool but not according to the wallet. Such an entry can be
  terminal, and rewriting the record for it buys nothing: the worst a
  restart can do is re-run the check once. Log it so it is diagnosable.

- Schedule the check on its own rather than running it from DoMaintenance
  ahead of the mixing gates. It keeps the same property - pending inputs
  unlock even while mixing or CoinJoin itself is disabled - with one
  cadence for both relay and block-only mode instead of once per second in
  one and once per minute in the other. Releasing these locks is pure
  bookkeeping: the outpoints are the ones the finalized mixing transaction
  spends, so by the time the wallet observes the spend they could not be
  selected again anyway.

- Move the timeout next to the other CoinJoin timeouts in coinjoin.h and
  restore the alphabetical include order.

- Mark the wrapped log format strings with /* Continued */ so lint-logs.py
  is satisfied, matching init.cpp and net_processing.cpp. It only inspects
  the first line of a log call and requires it to end with "\n".


_Trimmed to 38 lines — full report: https://github.com/dashpay/dash/commit/f9c4bebea16e4a91a45bbda63917c0da78e9ec77_
