# Q3930: Plasma checksum-cased address with wrong checksum via HotBridge (processWithdrawal)

## Question
Can an unprivileged user enter through `IntentsSDK.processWithdrawal` on the HotBridge route for Plasma with `destinationAddress` = `0xdAC17F958D2ee523a2206206994597C13D831ec8` (checksum-cased address with wrong checksum) and make `validateAddress` (`validateEthAddress`) accept a string that `hotSdk.buildGaslessWithdrawIntent` -> `mt_withdraw` on `v2_1.omni.hot.tg` with `receiver` then forwards unchanged, so the address the HOT Omni bridge relayer pays differs from the account the user controls and the withdrawal is lost?

## Target
- File/function: packages/intents-sdk/src/lib/validateAddress.ts `validateEthAddress`; packages/intents-sdk/src/bridges/hot-bridge/hot-bridge.ts `validateWithdrawal` / `createWithdrawalIntents`
- Entrypoint: `IntentsSDK.processWithdrawal` (end-to-end: estimate -> validate -> sign -> publish -> wait)
- Attacker controls: `destinationAddress` string (`0xdAC17F958D2ee523a2206206994597C13D831ec8`), `assetId` for a Plasma hot token, `destinationMemo`
- Exploit idea: `isAddress(strict:true)` rejects bad EIP-55 checksums; confirm all-lowercase bypass is intended and that the bridge receives lowercase. Encoding path: `hotSdk.buildGaslessWithdrawIntent` -> `mt_withdraw` on `v2_1.omni.hot.tg` with `receiver`.
- Invariant to test: For every string s where `validateAddress(s, 'eip155:9745')` is true, the payout address derived by the HOT Omni bridge relayer from the emitted intent must be the same account as s. Test: run validateAddress + createWithdrawalIntents on `0xdAC17F958D2ee523a2206206994597C13D831ec8` and inspect the emitted memo/recipient/receiver.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: call `validateAddress('0xdAC17F958D2ee523a2206206994597C13D831ec8', Chains.Plasma)`; then `createWithdrawalIntents` with mocked fee and assert the encoded destination byte-for-byte; compare against the hot bridge's documented accepted format.
