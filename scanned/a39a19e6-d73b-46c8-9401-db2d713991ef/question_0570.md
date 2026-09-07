# Q0570: BitcoinCash address containing a colon in payload via PoaBridge (createWithdrawalIntents)

## Question
If a counterparty supplies `destinationAddress` = `bitcoincash:qpm2qsznhks23z7629mms6s4cwef74vcwvy22gdx6a:extra` (address containing a colon in payload) for a BitcoinCash withdrawal via `IntentsSDK.createWithdrawalIntents`, does `validateBchAddress` return true while `createWithdrawIntentPrimitive` -> `ft_withdraw` to the `omft.near` token with memo `WITHDRAW_TO:<address>[:<memo>]` encodes a value the PoA bridge relayer (bridge.chaindefuser.com) interprets differently, breaking address-validated == address-paid?

## Target
- File/function: packages/intents-sdk/src/lib/validateAddress.ts `validateBchAddress`; packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts `validateWithdrawal` / `createWithdrawalIntents`
- Entrypoint: `IntentsSDK.createWithdrawalIntents` (returns raw `IntentPrimitive[]` for the integrator to sign with any signer)
- Attacker controls: `destinationAddress` string (`bitcoincash:qpm2qsznhks23z7629mms6s4cwef74vcwvy22gdx6a:extra`), `assetId` for a BitcoinCash poa token, `destinationMemo`
- Exploit idea: `createWithdrawMemo` joins with ':'; a second colon changes the memo split on the bridge side. Encoding path: `createWithdrawIntentPrimitive` -> `ft_withdraw` to the `omft.near` token with memo `WITHDRAW_TO:<address>[:<memo>]`.
- Invariant to test: For every string s where `validateAddress(s, 'bip122:000000000000000000651ef99cb9fcbe')` is true, the payout address derived by the PoA bridge relayer (bridge.chaindefuser.com) from the emitted intent must be the same account as s. Test: run validateAddress + createWithdrawalIntents on `bitcoincash:qpm2qsznhks23z7629mms6s4cwef74vcwvy22gdx6a:extra` and inspect the emitted memo/recipient/receiver.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: call `validateAddress('bitcoincash:qpm2qsznhks23z7629mms6s4cwef74vcwvy22gdx6a:extra', Chains.BitcoinCash)`; then `createWithdrawalIntents` with mocked fee and assert the encoded destination byte-for-byte; compare against the poa bridge's documented accepted format.
