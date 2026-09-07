# [?] fix(mint-client): add no-timeout OOB spend mode (#8740)

## Summary
Severity: Unknown
Chain: Fedimint
Component: fedimint/fedimint
Published: 2026-06-24
Source: https://github.com/fedimint/fedimint/commit/25f817be488764c062d6609144226a69f3b213fe
Type: security-commit

## Details
fix(mint-client): add no-timeout OOB spend mode (#8740)

Summary

Adds an opt-in no-timeout mode for Mint v1 out-of-band spends. Passing
`None` as the `try_cancel_after` argument to `spend_notes_with_selector`
disables automatic recovery/refund and makes `subscribe_spend_notes`
report the spend as complete immediately. Existing timeout callers pass
`Some(timeout)`.

Details

This keeps the API surface to one method while avoiding a public magic
timeout value. The no-timeout mode is recorded as a defaulted JSON
metadata field on `MintOperationMetaVariant::SpendOOB`, so old operation
metadata remains readable. In no-timeout mode, the spend still
atomically removes the notes and logs the OOB send event, but it does
not register an OOB refund state machine. `subscribe_spend_notes` yields
`Created` then `Success` directly, and `await_spend_oob_refund` returns
an empty `transaction_ids` list for this mode.

Reviewing

Potential problems to think through:

- In no-timeout mode the sender intentionally gives up both automatic
and manual reclaim through the OOB spend state machine. If the recipient
never reissues the notes, the normal timeout recovery safety net is
absent.
- The mode is tracked in operation-log JSON metadata, not in the OOB
state-machine encoding, so this avoids adding new persisted OOB state
variants.
- The `OOBNotesSpent` event timeout is now `Option<Duration>` and is
`None` when automatic refund is disabled.

Testing

- `just format`

_Trimmed to 38 lines — full report: https://github.com/fedimint/fedimint/commit/25f817be488764c062d6609144226a69f3b213fe_
