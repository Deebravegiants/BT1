# Q1404: Optimism the bridged token's own contract on destination via HotBridge (processWithdrawal)

## Question
If a counterparty supplies `destinationAddress` = `<token contract on chain>` (the bridged token's own contract on destination) for a Optimism withdrawal via `IntentsSDK.processWithdrawal`, does `validateEthAddress` return true while `hotSdk.buildGaslessWithdrawIntent` -> `mt_withdraw` on `v2_1.omni.hot.tg` with `receiver` encodes a value the HOT Omni bridge relayer interprets differently, breaking address-validated == address-paid?

## Target
- File/function: packages/intents-sdk/src/lib/validateAddress.ts `validateEthAddress`; packages/intents-sdk/src/bridges/hot-bridge/hot-bridge.ts `validateWithdrawal` / `createWithdrawalIntents`
- Entrypoint: `IntentsSDK.processWithdrawal` (end-to-end: estimate -> validate -> sign -> publish -> wait)
- Attacker controls: `destinationAddress` string (`<token contract on chain>`), `assetId` for a Optimism hot token, `destinationMemo`
- Exploit idea: `DestinationAddressMatchesTokenAddressError` relies on `origin_chain_address` / `getAddress(destTokenOmniAddress)`; a proxy or wrapper address passes. Encoding path: `hotSdk.buildGaslessWithdrawIntent` -> `mt_withdraw` on `v2_1.omni.hot.tg` with `receiver`.
- Invariant to test: For every string s where `validateAddress(s, 'eip155:10')` is true, the payout address derived by the HOT Omni bridge relayer from the emitted intent must be the same account as s. Test: run validateAddress + createWithdrawalIntents on `<token contract on chain>` and inspect the emitted memo/recipient/receiver.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: call `validateAddress('<token contract on chain>', Chains.Optimism)`; then `createWithdrawalIntents` with mocked fee and assert the encoded destination byte-for-byte; compare against the hot bridge's documented accepted format.
