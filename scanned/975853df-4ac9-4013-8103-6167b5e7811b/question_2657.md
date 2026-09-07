# Q2657: Adi checksum-cased address with wrong checksum via HotBridge (estimateWithdrawalFee)

## Question
If a counterparty supplies `destinationAddress` = `0xdAC17F958D2ee523a2206206994597C13D831ec8` (checksum-cased address with wrong checksum) for a Adi withdrawal via `IntentsSDK.estimateWithdrawalFee` with `amount: 0n, feeInclusive: false`, does `validateEthAddress` return true while `hotSdk.buildGaslessWithdrawIntent` -> `mt_withdraw` on `v2_1.omni.hot.tg` with `receiver` encodes a value the HOT Omni bridge relayer interprets differently, breaking address-validated == address-paid?

## Target
- File/function: packages/intents-sdk/src/lib/validateAddress.ts `validateEthAddress`; packages/intents-sdk/src/bridges/hot-bridge/hot-bridge.ts `validateWithdrawal` / `createWithdrawalIntents`
- Entrypoint: `IntentsSDK.estimateWithdrawalFee` with `amount: 0n, feeInclusive: false` (sets `skipMinAmountValidation` and still runs `validateWithdrawal`)
- Attacker controls: `destinationAddress` string (`0xdAC17F958D2ee523a2206206994597C13D831ec8`), `assetId` for a Adi hot token, `destinationMemo`
- Exploit idea: `isAddress(strict:true)` rejects bad EIP-55 checksums; confirm all-lowercase bypass is intended and that the bridge receives lowercase. Encoding path: `hotSdk.buildGaslessWithdrawIntent` -> `mt_withdraw` on `v2_1.omni.hot.tg` with `receiver`.
- Invariant to test: For every string s where `validateAddress(s, 'eip155:36900')` is true, the payout address derived by the HOT Omni bridge relayer from the emitted intent must be the same account as s. Test: run validateAddress + createWithdrawalIntents on `0xdAC17F958D2ee523a2206206994597C13D831ec8` and inspect the emitted memo/recipient/receiver.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: call `validateAddress('0xdAC17F958D2ee523a2206206994597C13D831ec8', Chains.Adi)`; then `createWithdrawalIntents` with mocked fee and assert the encoded destination byte-for-byte; compare against the hot bridge's documented accepted format.
