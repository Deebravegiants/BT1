# Q3662: Avalanche 0x000...dead in mixed case via HotBridge (estimateWithdrawalFee)

## Question
Can an unprivileged user enter through `IntentsSDK.estimateWithdrawalFee` with `amount: 0n, feeInclusive: false` on the HotBridge route for Avalanche with `destinationAddress` = `0x000000000000000000000000000000000000dEaD` (0x000...dead in mixed case) and make `validateAddress` (`validateEthAddress`) accept a string that `hotSdk.buildGaslessWithdrawIntent` -> `mt_withdraw` on `v2_1.omni.hot.tg` with `receiver` then forwards unchanged, so the address the HOT Omni bridge relayer pays differs from the account the user controls and the withdrawal is lost?

## Target
- File/function: packages/intents-sdk/src/lib/validateAddress.ts `validateEthAddress`; packages/intents-sdk/src/bridges/hot-bridge/hot-bridge.ts `validateWithdrawal` / `createWithdrawalIntents`
- Entrypoint: `IntentsSDK.estimateWithdrawalFee` with `amount: 0n, feeInclusive: false` (sets `skipMinAmountValidation` and still runs `validateWithdrawal`)
- Attacker controls: `destinationAddress` string (`0x000000000000000000000000000000000000dEaD`), `assetId` for a Avalanche hot token, `destinationMemo`
- Exploit idea: rejected via toLowerCase compare; check `0x0000000000000000000000000000000000000001` and precompiles pass. Encoding path: `hotSdk.buildGaslessWithdrawIntent` -> `mt_withdraw` on `v2_1.omni.hot.tg` with `receiver`.
- Invariant to test: For every string s where `validateAddress(s, 'eip155:43114')` is true, the payout address derived by the HOT Omni bridge relayer from the emitted intent must be the same account as s. Test: run validateAddress + createWithdrawalIntents on `0x000000000000000000000000000000000000dEaD` and inspect the emitted memo/recipient/receiver.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: call `validateAddress('0x000000000000000000000000000000000000dEaD', Chains.Avalanche)`; then `createWithdrawalIntents` with mocked fee and assert the encoded destination byte-for-byte; compare against the hot bridge's documented accepted format.
