# Q0471: BitcoinCash CashAddr without prefix, uppercase via PoaBridge (signAndSendWithdrawalIntent)

## Question
Using `IntentsSDK.signAndSendWithdrawalIntent` with a caller-supplied `feeEstimation` for `BitcoinCash`, can `QPM2QSZNHKS23Z7629MMS6S4CWEF74VCWVY22GDX6A` (CashAddr without prefix, uppercase) pass `validateBchAddress` and reach `createWithdrawIntentPrimitive` -> `ft_withdraw` to the `omft.near` token with memo `WITHDRAW_TO:<address>[:<memo>]` so that the destination on chain is not the one validated, given that normalisation lowercases then re-prefixes; the memo receives the original-case string?

## Target
- File/function: packages/intents-sdk/src/lib/validateAddress.ts `validateBchAddress`; packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts `validateWithdrawal` / `createWithdrawalIntents`
- Entrypoint: `IntentsSDK.signAndSendWithdrawalIntent` with a caller-supplied `feeEstimation` (skips `_estimateWithdrawalFee`'s `FeeExceedsAmountError` and re-validates only inside `createWithdrawalIntents`)
- Attacker controls: `destinationAddress` string (`QPM2QSZNHKS23Z7629MMS6S4CWEF74VCWVY22GDX6A`), `assetId` for a BitcoinCash poa token, `destinationMemo`
- Exploit idea: normalisation lowercases then re-prefixes; the memo receives the original-case string. Encoding path: `createWithdrawIntentPrimitive` -> `ft_withdraw` to the `omft.near` token with memo `WITHDRAW_TO:<address>[:<memo>]`.
- Invariant to test: For every string s where `validateAddress(s, 'bip122:000000000000000000651ef99cb9fcbe')` is true, the payout address derived by the PoA bridge relayer (bridge.chaindefuser.com) from the emitted intent must be the same account as s. Test: run validateAddress + createWithdrawalIntents on `QPM2QSZNHKS23Z7629MMS6S4CWEF74VCWVY22GDX6A` and inspect the emitted memo/recipient/receiver.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: call `validateAddress('QPM2QSZNHKS23Z7629MMS6S4CWEF74VCWVY22GDX6A', Chains.BitcoinCash)`; then `createWithdrawalIntents` with mocked fee and assert the encoded destination byte-for-byte; compare against the poa bridge's documented accepted format.
