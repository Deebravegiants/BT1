# Q5304: TON bounceable vs non-bounceable same account via HotBridge (signAndSendWithdrawalIntent)

## Question
If a counterparty supplies `destinationAddress` = `UQBkxBWE4Gf9gd2sNbm1SJ6zXWnbA6ywoBvpAUQhBXJY_YiM` (bounceable vs non-bounceable same account) for a TON withdrawal via `IntentsSDK.signAndSendWithdrawalIntent` with a caller-supplied `feeEstimation`, does `validateTonAddress` return true while `hotSdk.buildGaslessWithdrawIntent` -> `mt_withdraw` on `v2_1.omni.hot.tg` with `receiver` encodes a value the HOT Omni bridge relayer interprets differently, breaking address-validated == address-paid?

## Target
- File/function: packages/intents-sdk/src/lib/validateAddress.ts `validateTonAddress`; packages/intents-sdk/src/bridges/hot-bridge/hot-bridge.ts `validateWithdrawal` / `createWithdrawalIntents`
- Entrypoint: `IntentsSDK.signAndSendWithdrawalIntent` with a caller-supplied `feeEstimation` (skips `_estimateWithdrawalFee`'s `FeeExceedsAmountError` and re-validates only inside `createWithdrawalIntents`)
- Attacker controls: `destinationAddress` string (`UQBkxBWE4Gf9gd2sNbm1SJ6zXWnbA6ywoBvpAUQhBXJY_YiM`), `assetId` for a TON hot token, `destinationMemo`
- Exploit idea: `compareTonAddress` treats them equal; check HOT's `receiver` handling of non-bounceable for uninitialised wallets. Encoding path: `hotSdk.buildGaslessWithdrawIntent` -> `mt_withdraw` on `v2_1.omni.hot.tg` with `receiver`.
- Invariant to test: For every string s where `validateAddress(s, 'tvm:-239')` is true, the payout address derived by the HOT Omni bridge relayer from the emitted intent must be the same account as s. Test: run validateAddress + createWithdrawalIntents on `UQBkxBWE4Gf9gd2sNbm1SJ6zXWnbA6ywoBvpAUQhBXJY_YiM` and inspect the emitted memo/recipient/receiver.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: call `validateAddress('UQBkxBWE4Gf9gd2sNbm1SJ6zXWnbA6ywoBvpAUQhBXJY_YiM', Chains.TON)`; then `createWithdrawalIntents` with mocked fee and assert the encoded destination byte-for-byte; compare against the hot bridge's documented accepted format.
