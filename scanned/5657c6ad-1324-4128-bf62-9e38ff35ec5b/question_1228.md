# Q1228: PoA status nep141:arb-0xaf88d065e77c8cc: `withdrawal_status` returns `COMPLET

## Question
For PoA token `nep141:arb-0xaf88d065e77c8cc2239327c5edb3a432268e5831.omft.near`, when `withdrawal_status` returns `COMPLETED` with `transfer_tx_hash: null`, does `PoaBridge.describeWithdrawal` (`findMatchingWithdrawal` by assetId, `getWithdrawalStatusWithRetry`) attach the wrong withdrawal's status/txHash to the user's `WithdrawalIdentifier`, so an integrator sees `completed` for a payout that went to the other destination?

## Target
- File/function: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts `describeWithdrawal`, `findMatchingWithdrawal`, `getWithdrawalStatusWithRetry`
- Entrypoint: `IntentsSDK.waitForWithdrawalCompletion`
- Attacker controls: batch composition with repeated assetId
- Exploit idea: Matching is by `nep141:<near_token_id>` only; the code comment admits multiple same-token withdrawals are unsupported yet the SDK accepts such batches.
- Invariant to test: each WithdrawalIdentifier resolves to the withdrawal with the same destination address and amount.
- Expected Immunefi impact: High - status/hash misreport making an integrator credit or refund twice (HackenProof: withdrawal processing / serialization correctness)
- Fast validation: vitest: mock `withdrawal_status` with two entries for the same token and assert both identifiers get distinct results or an error.
