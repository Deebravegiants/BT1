# Q0442: BitcoinCash legacy 3... address via PoaBridge (createWithdrawalIntents)

## Question
Can an unprivileged user enter through `IntentsSDK.createWithdrawalIntents` on the PoaBridge route for BitcoinCash with `destinationAddress` = `3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy` (legacy 3... address) and make `validateAddress` (`validateBchAddress`) accept a string that `createWithdrawIntentPrimitive` -> `ft_withdraw` to the `omft.near` token with memo `WITHDRAW_TO:<address>[:<memo>]` then forwards unchanged, so the address the PoA bridge relayer (bridge.chaindefuser.com) pays differs from the account the user controls and the withdrawal is lost?

## Target
- File/function: packages/intents-sdk/src/lib/validateAddress.ts `validateBchAddress`; packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts `validateWithdrawal` / `createWithdrawalIntents`
- Entrypoint: `IntentsSDK.createWithdrawalIntents` (returns raw `IntentPrimitive[]` for the integrator to sign with any signer)
- Attacker controls: `destinationAddress` string (`3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy`), `assetId` for a BitcoinCash poa token, `destinationMemo`
- Exploit idea: shared with Bitcoin P2SH; regex-only acceptance and no BCH-specific check. Encoding path: `createWithdrawIntentPrimitive` -> `ft_withdraw` to the `omft.near` token with memo `WITHDRAW_TO:<address>[:<memo>]`.
- Invariant to test: For every string s where `validateAddress(s, 'bip122:000000000000000000651ef99cb9fcbe')` is true, the payout address derived by the PoA bridge relayer (bridge.chaindefuser.com) from the emitted intent must be the same account as s. Test: run validateAddress + createWithdrawalIntents on `3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy` and inspect the emitted memo/recipient/receiver.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: call `validateAddress('3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy', Chains.BitcoinCash)`; then `createWithdrawalIntents` with mocked fee and assert the encoded destination byte-for-byte; compare against the poa bridge's documented accepted format.
