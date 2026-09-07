# Q1661: BNB the bridged token's own contract on destination via HotBridge (processWithdrawal)

## Question
Can an unprivileged user enter through `IntentsSDK.processWithdrawal` on the HotBridge route for BNB with `destinationAddress` = `<token contract on chain>` (the bridged token's own contract on destination) and make `validateAddress` (`validateEthAddress`) accept a string that `hotSdk.buildGaslessWithdrawIntent` -> `mt_withdraw` on `v2_1.omni.hot.tg` with `receiver` then forwards unchanged, so the address the HOT Omni bridge relayer pays differs from the account the user controls and the withdrawal is lost?

## Target
- File/function: packages/intents-sdk/src/lib/validateAddress.ts `validateEthAddress`; packages/intents-sdk/src/bridges/hot-bridge/hot-bridge.ts `validateWithdrawal` / `createWithdrawalIntents`
- Entrypoint: `IntentsSDK.processWithdrawal` (end-to-end: estimate -> validate -> sign -> publish -> wait)
- Attacker controls: `destinationAddress` string (`<token contract on chain>`), `assetId` for a BNB hot token, `destinationMemo`
- Exploit idea: `DestinationAddressMatchesTokenAddressError` relies on `origin_chain_address` / `getAddress(destTokenOmniAddress)`; a proxy or wrapper address passes. Encoding path: `hotSdk.buildGaslessWithdrawIntent` -> `mt_withdraw` on `v2_1.omni.hot.tg` with `receiver`.
- Invariant to test: For every string s where `validateAddress(s, 'eip155:56')` is true, the payout address derived by the HOT Omni bridge relayer from the emitted intent must be the same account as s. Test: run validateAddress + createWithdrawalIntents on `<token contract on chain>` and inspect the emitted memo/recipient/receiver.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: call `validateAddress('<token contract on chain>', Chains.BNB)`; then `createWithdrawalIntents` with mocked fee and assert the encoded destination byte-for-byte; compare against the hot bridge's documented accepted format.
