# Q5281: TON raw address with 0x prefix on hash via HotBridge (createWithdrawalIntents)

## Question
Can an unprivileged user enter through `IntentsSDK.createWithdrawalIntents` on the HotBridge route for TON with `destinationAddress` = `0:0x64c41584e067fd81ddac35b9b5489eb35d69db03acb0a01be9014421057258fd` (raw address with 0x prefix on hash) and make `validateAddress` (`validateTonAddress`) accept a string that `hotSdk.buildGaslessWithdrawIntent` -> `mt_withdraw` on `v2_1.omni.hot.tg` with `receiver` then forwards unchanged, so the address the HOT Omni bridge relayer pays differs from the account the user controls and the withdrawal is lost?

## Target
- File/function: packages/intents-sdk/src/lib/validateAddress.ts `validateTonAddress`; packages/intents-sdk/src/bridges/hot-bridge/hot-bridge.ts `validateWithdrawal` / `createWithdrawalIntents`
- Entrypoint: `IntentsSDK.createWithdrawalIntents` (returns raw `IntentPrimitive[]` for the integrator to sign with any signer)
- Attacker controls: `destinationAddress` string (`0:0x64c41584e067fd81ddac35b9b5489eb35d69db03acb0a01be9014421057258fd`), `assetId` for a TON hot token, `destinationMemo`
- Exploit idea: `parseTonRawAddress` strips 0x; the un-stripped string is what HOT receives. Encoding path: `hotSdk.buildGaslessWithdrawIntent` -> `mt_withdraw` on `v2_1.omni.hot.tg` with `receiver`.
- Invariant to test: For every string s where `validateAddress(s, 'tvm:-239')` is true, the payout address derived by the HOT Omni bridge relayer from the emitted intent must be the same account as s. Test: run validateAddress + createWithdrawalIntents on `0:0x64c41584e067fd81ddac35b9b5489eb35d69db03acb0a01be9014421057258fd` and inspect the emitted memo/recipient/receiver.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: call `validateAddress('0:0x64c41584e067fd81ddac35b9b5489eb35d69db03acb0a01be9014421057258fd', Chains.TON)`; then `createWithdrawalIntents` with mocked fee and assert the encoded destination byte-for-byte; compare against the hot bridge's documented accepted format.
