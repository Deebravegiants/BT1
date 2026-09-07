# Q5731: Stellar account without trustline for the asset via HotBridge (signAndSendWithdrawalIntent)

## Question
Using `IntentsSDK.signAndSendWithdrawalIntent` with a caller-supplied `feeEstimation` for `Stellar`, can `GA5ZSEJYB37JRC5AVCIA5MOP4RHTM335X2KGX3IHOJAPP5RE34K4KZVN` (account without trustline for the asset) pass `validateStellarAddress` and reach `hotSdk.buildGaslessWithdrawIntent` -> `mt_withdraw` on `v2_1.omni.hot.tg` with `receiver` so that the destination on chain is not the one validated, given that `TrustlineNotFoundError` only for non-native; check native XLM path and `token` value passed?

## Target
- File/function: packages/intents-sdk/src/lib/validateAddress.ts `validateStellarAddress`; packages/intents-sdk/src/bridges/hot-bridge/hot-bridge.ts `validateWithdrawal` / `createWithdrawalIntents`
- Entrypoint: `IntentsSDK.signAndSendWithdrawalIntent` with a caller-supplied `feeEstimation` (skips `_estimateWithdrawalFee`'s `FeeExceedsAmountError` and re-validates only inside `createWithdrawalIntents`)
- Attacker controls: `destinationAddress` string (`GA5ZSEJYB37JRC5AVCIA5MOP4RHTM335X2KGX3IHOJAPP5RE34K4KZVN`), `assetId` for a Stellar hot token, `destinationMemo`
- Exploit idea: `TrustlineNotFoundError` only for non-native; check native XLM path and `token` value passed. Encoding path: `hotSdk.buildGaslessWithdrawIntent` -> `mt_withdraw` on `v2_1.omni.hot.tg` with `receiver`.
- Invariant to test: For every string s where `validateAddress(s, 'stellar:pubnet')` is true, the payout address derived by the HOT Omni bridge relayer from the emitted intent must be the same account as s. Test: run validateAddress + createWithdrawalIntents on `GA5ZSEJYB37JRC5AVCIA5MOP4RHTM335X2KGX3IHOJAPP5RE34K4KZVN` and inspect the emitted memo/recipient/receiver.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: call `validateAddress('GA5ZSEJYB37JRC5AVCIA5MOP4RHTM335X2KGX3IHOJAPP5RE34K4KZVN', Chains.Stellar)`; then `createWithdrawalIntents` with mocked fee and assert the encoded destination byte-for-byte; compare against the hot bridge's documented accepted format.
