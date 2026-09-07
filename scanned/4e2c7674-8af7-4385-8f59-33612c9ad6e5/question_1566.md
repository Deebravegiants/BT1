# Q1566: PoA min/fee nep141:xrp.omft.near: `tokens.find(t => t.intents_token_id =

## Question
For PoA token `nep141:xrp.omft.near` (XRPL), when `tokens.find(t => t.intents_token_id === assetId)` misses because the list is keyed by a different chain string from `toPoaNetwork`, can an unprivileged user sign a withdrawal below the bridge's real minimum or with a fee the bridge will not honour, so the PoA relayer marks it failed/pending indefinitely while intents.near already debited the tokens?

## Target
- File/function: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts `validateWithdrawal` (min check, getCachedSupportedTokens), `estimateWithdrawalFee`, `createWithdrawalIntents`
- Entrypoint: `IntentsSDK.processWithdrawal`
- Attacker controls: `amount`, timing relative to cache TTL, `assetId`
- Exploit idea: Min and fee come from two different PoA endpoints at two different times; the intent amount is fee-adjusted after validation.
- Invariant to test: signed amount - relayerFee >= live min_withdrawal_amount and relayerFee == live withdrawal fee at execution.
- Expected Immunefi impact: High - withdrawal stuck or refunded to the wrong account until manual intervention (HackenProof: withdrawal processing; Immunefi class: temporary freezing of funds)
- Fast validation: vitest: mock `supported_tokens` and `withdrawal_estimate` with divergent values; assert acceptance.
