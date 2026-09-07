# Q5056: XRPL X-address with embedded tag via PoaBridge (createWithdrawalIntents)

## Question
Using `IntentsSDK.createWithdrawalIntents` for `XRPL`, can `XVLhHMPHU98es4dbozjVtdWzVrDjtV18pX8yuPT7y4xaEHi` (X-address with embedded tag) pass `validateXrpAddress` and reach `createWithdrawIntentPrimitive` -> `ft_withdraw` to the `omft.near` token with memo `WITHDRAW_TO:<address>[:<memo>]` so that the destination on chain is not the one validated, given that `isValidXAddress` accepted; the embedded tag and a separate `destinationMemo` can disagree?

## Target
- File/function: packages/intents-sdk/src/lib/validateAddress.ts `validateXrpAddress`; packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts `validateWithdrawal` / `createWithdrawalIntents`
- Entrypoint: `IntentsSDK.createWithdrawalIntents` (returns raw `IntentPrimitive[]` for the integrator to sign with any signer)
- Attacker controls: `destinationAddress` string (`XVLhHMPHU98es4dbozjVtdWzVrDjtV18pX8yuPT7y4xaEHi`), `assetId` for a XRPL poa token, `destinationMemo`
- Exploit idea: `isValidXAddress` accepted; the embedded tag and a separate `destinationMemo` can disagree. Encoding path: `createWithdrawIntentPrimitive` -> `ft_withdraw` to the `omft.near` token with memo `WITHDRAW_TO:<address>[:<memo>]`.
- Invariant to test: For every string s where `validateAddress(s, 'xrpl:0')` is true, the payout address derived by the PoA bridge relayer (bridge.chaindefuser.com) from the emitted intent must be the same account as s. Test: run validateAddress + createWithdrawalIntents on `XVLhHMPHU98es4dbozjVtdWzVrDjtV18pX8yuPT7y4xaEHi` and inspect the emitted memo/recipient/receiver.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: call `validateAddress('XVLhHMPHU98es4dbozjVtdWzVrDjtV18pX8yuPT7y4xaEHi', Chains.XRPL)`; then `createWithdrawalIntents` with mocked fee and assert the encoded destination byte-for-byte; compare against the poa bridge's documented accepted format.
