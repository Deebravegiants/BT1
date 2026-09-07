# Q2351: Monad 0x000...dead in mixed case via HotBridge (signAndSendWithdrawalIntent)

## Question
If a counterparty supplies `destinationAddress` = `0x000000000000000000000000000000000000dEaD` (0x000...dead in mixed case) for a Monad withdrawal via `IntentsSDK.signAndSendWithdrawalIntent` with a caller-supplied `feeEstimation`, does `validateEthAddress` return true while `hotSdk.buildGaslessWithdrawIntent` -> `mt_withdraw` on `v2_1.omni.hot.tg` with `receiver` encodes a value the HOT Omni bridge relayer interprets differently, breaking address-validated == address-paid?

## Target
- File/function: packages/intents-sdk/src/lib/validateAddress.ts `validateEthAddress`; packages/intents-sdk/src/bridges/hot-bridge/hot-bridge.ts `validateWithdrawal` / `createWithdrawalIntents`
- Entrypoint: `IntentsSDK.signAndSendWithdrawalIntent` with a caller-supplied `feeEstimation` (skips `_estimateWithdrawalFee`'s `FeeExceedsAmountError` and re-validates only inside `createWithdrawalIntents`)
- Attacker controls: `destinationAddress` string (`0x000000000000000000000000000000000000dEaD`), `assetId` for a Monad hot token, `destinationMemo`
- Exploit idea: rejected via toLowerCase compare; check `0x0000000000000000000000000000000000000001` and precompiles pass. Encoding path: `hotSdk.buildGaslessWithdrawIntent` -> `mt_withdraw` on `v2_1.omni.hot.tg` with `receiver`.
- Invariant to test: For every string s where `validateAddress(s, 'eip155:143')` is true, the payout address derived by the HOT Omni bridge relayer from the emitted intent must be the same account as s. Test: run validateAddress + createWithdrawalIntents on `0x000000000000000000000000000000000000dEaD` and inspect the emitted memo/recipient/receiver.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: call `validateAddress('0x000000000000000000000000000000000000dEaD', Chains.Monad)`; then `createWithdrawalIntents` with mocked fee and assert the encoded destination byte-for-byte; compare against the hot bridge's documented accepted format.
