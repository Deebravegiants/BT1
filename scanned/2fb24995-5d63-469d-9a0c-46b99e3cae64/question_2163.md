# Q2163: PoA status nep141:tron-d28a265909efecdc: a withdrawal of this token plus a Di

## Question
For PoA token `nep141:tron-d28a265909efecdcee7c5028585214ea0b96f015.omft.near`, when a withdrawal of this token plus a Direct-route withdrawal of the same nep141 id, does `PoaBridge.describeWithdrawal` (`findMatchingWithdrawal` by assetId, `getWithdrawalStatusWithRetry`) attach the wrong withdrawal's status/txHash to the user's `WithdrawalIdentifier`, so an integrator sees `completed` for a payout that went to the other destination?

## Target
- File/function: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts `describeWithdrawal`, `findMatchingWithdrawal`, `getWithdrawalStatusWithRetry`
- Entrypoint: `IntentsSDK.waitForWithdrawalCompletion`
- Attacker controls: batch composition with repeated assetId
- Exploit idea: Matching is by `nep141:<near_token_id>` only; the code comment admits multiple same-token withdrawals are unsupported yet the SDK accepts such batches.
- Invariant to test: each WithdrawalIdentifier resolves to the withdrawal with the same destination address and amount.
- Expected Immunefi impact: High - status/hash misreport making an integrator credit or refund twice (HackenProof: withdrawal processing / serialization correctness)
- Fast validation: vitest: mock `withdrawal_status` with two entries for the same token and assert both identifiers get distinct results or an error.
