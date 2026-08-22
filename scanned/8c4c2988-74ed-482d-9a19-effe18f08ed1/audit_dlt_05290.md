# [?] fix(wallet): reject peg-out amounts that overflow the selection arithmetic

## Summary
Severity: Unknown
Chain: Fedimint
Component: fedimint/fedimint
Published: 2026-08-06
Source: https://github.com/fedimint/fedimint/commit/03131e9e191379f63ce07e04141dc87432d5b75e
Type: security-commit

## Details
fix(wallet): reject peg-out amounts that overflow the selection arithmetic

`bitcoin::Amount`'s `Add` is `checked_add(..).expect("Amount addition
error")` with no `MAX_MONEY` clamp, and the UTXO selection loop summed
`peg_out_amount + change_script.minimal_non_dust() + fees` with it. Two
routes fed that sum an unvalidated amount:

  * `PEG_OUT_FEES_ENDPOINT` is a public, unauthenticated endpoint that
    hands the caller's raw `u64` to `bitcoin::Amount::from_sat`. A single
    anonymous call with `sats = u64::MAX` panicked the handler.
  * `process_output` passes `peg_out.amount` to `create_peg_out_tx`
    verbatim and only runs `validate_tx` afterwards.

On the iroh transport a panicking handler takes the guardian process
down, so route one alone was a remote kill switch.

Reject amounts above `MAX_MONEY` up front in `create_tx` -- the single
choke point both routes pass through -- and make the loop's target
computation checked, since fees are not bounded by `MAX_MONEY` and grow
with every selected input. Both cases report `NotEnoughSpendableUTXO`,
which is literally accurate: no federation UTXO set can fund an amount
that cannot exist on chain. Reusing the existing variant also keeps
`WalletOutputError` wire-compatible, so older clients still decode the
submission outcome.

Consensus safety of the `process_output` route: turning a panic into a
rejection changes transaction validity, so it has to be argued rather
than assumed. `bitcoin::Amount`'s `Add` panics in every build profile,
so an output whose amount overflowed that sum panicked every guardian at
the same ordered item and panicked them again on every restart,
permanently halting the federation at that session. A federation that is
still running therefore has no such transaction in its history, and the
new rejection can only ever fire on a transaction that would previously
have bricked the federation instead of being accepted. The rejection is
also behaviour-preserving on every execution that previously returned
`Ok`: `total_selected_value` is a sum of confirmed chain outputs and so
is bounded by the money supply, meaning any amount above `MAX_MONEY`
would have exhausted the UTXO set and returned the very same error. No

_Trimmed to 38 lines — full report: https://github.com/fedimint/fedimint/commit/03131e9e191379f63ce07e04141dc87432d5b75e_
