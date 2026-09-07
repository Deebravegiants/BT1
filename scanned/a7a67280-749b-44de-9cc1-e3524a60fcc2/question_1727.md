# Q1727: BNB an address that is a contract without receive() via HotBridge (processWithdrawal)

## Question
Can an unprivileged user enter through `IntentsSDK.processWithdrawal` on the HotBridge route for BNB with `destinationAddress` = `0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984` (an address that is a contract without receive()) and make `validateAddress` (`validateEthAddress`) accept a string that `hotSdk.buildGaslessWithdrawIntent` -> `mt_withdraw` on `v2_1.omni.hot.tg` with `receiver` then forwards unchanged, so the address the HOT Omni bridge relayer pays differs from the account the user controls and the withdrawal is lost?

## Target
- File/function: packages/intents-sdk/src/lib/validateAddress.ts `validateEthAddress`; packages/intents-sdk/src/bridges/hot-bridge/hot-bridge.ts `validateWithdrawal` / `createWithdrawalIntents`
- Entrypoint: `IntentsSDK.processWithdrawal` (end-to-end: estimate -> validate -> sign -> publish -> wait)
- Attacker controls: `destinationAddress` string (`0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984`), `assetId` for a BNB hot token, `destinationMemo`
- Exploit idea: format-only validation; native withdrawals to non-payable contracts revert on destination and may strand funds at the bridge. Encoding path: `hotSdk.buildGaslessWithdrawIntent` -> `mt_withdraw` on `v2_1.omni.hot.tg` with `receiver`.
- Invariant to test: For every string s where `validateAddress(s, 'eip155:56')` is true, the payout address derived by the HOT Omni bridge relayer from the emitted intent must be the same account as s. Test: run validateAddress + createWithdrawalIntents on `0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984` and inspect the emitted memo/recipient/receiver.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: call `validateAddress('0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984', Chains.BNB)`; then `createWithdrawalIntents` with mocked fee and assert the encoded destination byte-for-byte; compare against the hot bridge's documented accepted format.
