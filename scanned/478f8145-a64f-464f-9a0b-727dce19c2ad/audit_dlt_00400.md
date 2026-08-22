# [?] [security] make coin reservation rewriter fallible to fix dryRun/devInspect panic (#26528)

## Summary
Severity: Unknown
Chain: Sui
Component: MystenLabs/sui
Published: 2026-05-07
Source: https://github.com/MystenLabs/sui/commit/9e52010210244236dc824d74e74b40eb1a604ab0
Type: security-commit

## Details
[security] make coin reservation rewriter fallible to fix dryRun/devInspect panic (#26528)

## Summary

`rewrite_transaction_for_coin_reservations` previously called
`.unwrap()` on the coin-reservation resolution result, assuming the
input had been validated upstream. That assumption holds for certified
transactions but **not** for `dryRunTransactionBlock` and
`devInspectTransactionBlock`, which accept arbitrary client-supplied
transaction kinds without prior reservation validation. A client could
submit a fake coin reservation (an `ImmOrOwnedObject` whose `ObjectRef`
matches the masked-coin-reservation encoding but references a
non-existent accumulator) and panic the fullnode thread handling the
dry-run.

This PR:

- Makes `rewrite_transaction_for_coin_reservations` return
`UserInputResult<Option<Vec<bool>>>` so the resolver error surfaces as a
normal user-input error.
- Plumbs the result through both certificate execution (where we still
`expect()` since validation guarantees success) and the dry-run /
dev-inspect paths (where the error is propagated to the client).
- Moves rewriting out of the inner `execute_transaction_to_effects`
helper into each caller, since the certificate path can panic on failure
while the dry-run paths must not.
- Adds 4 e2e simtests under `address_balance_compatibility_tests`:
  - `test_fake_coin_reservation_dry_run_does_not_panic`
  - `test_fake_coin_reservation_dev_inspect_does_not_panic`
  - `test_fake_coin_reservation_dry_run_safe_when_flag_disabled`
  - `test_fake_coin_reservation_dev_inspect_safe_when_flag_disabled`

## Verification

Reverted the fix locally (test commit only) and ran the new tests:
```
FAIL sui-e2e-tests::address_balance_compatibility_tests test_fake_coin_reservation_dev_inspect_does_not_panic
FAIL sui-e2e-tests::address_balance_compatibility_tests test_fake_coin_reservation_dry_run_does_not_panic
```

_Trimmed to 38 lines — full report: https://github.com/MystenLabs/sui/commit/9e52010210244236dc824d74e74b40eb1a604ab0_
