# Q4454: PoA min/fee nep141:gnosis-0xe91d153e0b41: `min_withdrawal_amount` is checked aga

## Question
For PoA token `nep141:gnosis-0xe91d153e0b41518a2ce8dd3d7944fa863463a97d.omft.near` (Gnosis), when `min_withdrawal_amount` is checked against `actualAmount` but the intent carries `actualAmount + relayerFee`, can an unprivileged user sign a withdrawal below the bridge's real minimum or with a fee the bridge will not honour, so the PoA relayer marks it failed/pending indefinitely while intents.near already debited the tokens?

## Target
- File/function: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts `validateWithdrawal` (min check, getCachedSupportedTokens), `estimateWithdrawalFee`, `createWithdrawalIntents`
- Entrypoint: `IntentsSDK.processWithdrawal`
- Attacker controls: `amount`, timing relative to cache TTL, `assetId`
- Exploit idea: Min and fee come from two different PoA endpoints at two different times; the intent amount is fee-adjusted after validation.
- Invariant to test: signed amount - relayerFee >= live min_withdrawal_amount and relayerFee == live withdrawal fee at execution.
- Expected Immunefi impact: High - withdrawal stuck or refunded to the wrong account until manual intervention (HackenProof: withdrawal processing; Immunefi class: temporary freezing of funds)
- Fast validation: vitest: mock `supported_tokens` and `withdrawal_estimate` with divergent values; assert acceptance.
