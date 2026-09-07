# Q5249: TON user-friendly testnet-tag address via HotBridge (createWithdrawalIntents)

## Question
Using `IntentsSDK.createWithdrawalIntents` for `TON`, can `kQBkxBWE4Gf9gd2sNbm1SJ6zXWnbA6ywoBvpAUQhBXJY_dNJ` (user-friendly testnet-tag address) pass `validateTonAddress` and reach `hotSdk.buildGaslessWithdrawIntent` -> `mt_withdraw` on `v2_1.omni.hot.tg` with `receiver` so that the destination on chain is not the one validated, given that tag 0x91 rejected; check `tag === null` shortcut for raw form bypasses tag policy?

## Target
- File/function: packages/intents-sdk/src/lib/validateAddress.ts `validateTonAddress`; packages/intents-sdk/src/bridges/hot-bridge/hot-bridge.ts `validateWithdrawal` / `createWithdrawalIntents`
- Entrypoint: `IntentsSDK.createWithdrawalIntents` (returns raw `IntentPrimitive[]` for the integrator to sign with any signer)
- Attacker controls: `destinationAddress` string (`kQBkxBWE4Gf9gd2sNbm1SJ6zXWnbA6ywoBvpAUQhBXJY_dNJ`), `assetId` for a TON hot token, `destinationMemo`
- Exploit idea: tag 0x91 rejected; check `tag === null` shortcut for raw form bypasses tag policy. Encoding path: `hotSdk.buildGaslessWithdrawIntent` -> `mt_withdraw` on `v2_1.omni.hot.tg` with `receiver`.
- Invariant to test: For every string s where `validateAddress(s, 'tvm:-239')` is true, the payout address derived by the HOT Omni bridge relayer from the emitted intent must be the same account as s. Test: run validateAddress + createWithdrawalIntents on `kQBkxBWE4Gf9gd2sNbm1SJ6zXWnbA6ywoBvpAUQhBXJY_dNJ` and inspect the emitted memo/recipient/receiver.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: call `validateAddress('kQBkxBWE4Gf9gd2sNbm1SJ6zXWnbA6ywoBvpAUQhBXJY_dNJ', Chains.TON)`; then `createWithdrawalIntents` with mocked fee and assert the encoded destination byte-for-byte; compare against the hot bridge's documented accepted format.
