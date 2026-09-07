# Q2453: Internal transfer nep141:arb-0xaf88d065e77c8: `destinationAddress` = an implicit a

## Question
Using `createInternalTransferRoute()` with `assetId` = `nep141:arb-0xaf88d065e77c8cc2239327c5edb3a432268e5831.omft.near` and `destinationAddress` = an implicit account (64-hex) with no key, does `IntentsBridge.createWithdrawalIntents` emit `transfer` with `tokens: {'nep141:arb-0xaf88d065e77c8cc2239327c5edb3a432268e5831.omft.near': amount}` to that `receiver_id` after only `validateAddress(destinationAddress, Chains.Near)`, and does `describeWithdrawal` return `completed` immediately, so the balance moves to an account nobody controls while the integrator sees success?

## Target
- File/function: packages/intents-sdk/src/bridges/intents-bridge/intents-bridge.ts `createWithdrawalIntents`, `validateWithdrawal`, `describeWithdrawal`
- Entrypoint: `IntentsSDK.processWithdrawal` with `createInternalTransferRoute()`
- Attacker controls: `destinationAddress` (any NEAR-format id), `assetId`, `destinationMemo`
- Exploit idea: No existence or type check for the receiver; `transfer` moves internal balance inside intents.near.
- Invariant to test: receiver_id is an account the user intends and can operate; funds transferred == amount; status reflects on-chain result.
- Expected Immunefi impact: High - withdrawal stuck or refunded to the wrong account until manual intervention (HackenProof: withdrawal processing; Immunefi class: temporary freezing of funds)
- Fast validation: vitest: build intents for each receiver and inspect; confirm no RPC existence check is performed.
