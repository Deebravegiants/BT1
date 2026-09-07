# Q0947: Litecoin bech32m taproot ltc1p via PoaBridge (processWithdrawal)

## Question
Using `IntentsSDK.processWithdrawal` for `Litecoin`, can `ltc1pqar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq2ka6yp` (bech32m taproot ltc1p) pass `validateLitecoinAddress` and reach `createWithdrawIntentPrimitive` -> `ft_withdraw` to the `omft.near` token with memo `WITHDRAW_TO:<address>[:<memo>]` so that the destination on chain is not the one validated, given that accepted when 32 bytes; PoA payout support for LTC taproot is unverified?

## Target
- File/function: packages/intents-sdk/src/lib/validateAddress.ts `validateLitecoinAddress`; packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts `validateWithdrawal` / `createWithdrawalIntents`
- Entrypoint: `IntentsSDK.processWithdrawal` (end-to-end: estimate -> validate -> sign -> publish -> wait)
- Attacker controls: `destinationAddress` string (`ltc1pqar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq2ka6yp`), `assetId` for a Litecoin poa token, `destinationMemo`
- Exploit idea: accepted when 32 bytes; PoA payout support for LTC taproot is unverified. Encoding path: `createWithdrawIntentPrimitive` -> `ft_withdraw` to the `omft.near` token with memo `WITHDRAW_TO:<address>[:<memo>]`.
- Invariant to test: For every string s where `validateAddress(s, 'bip122:12a765e31ffd4059bada1e25190f6e98')` is true, the payout address derived by the PoA bridge relayer (bridge.chaindefuser.com) from the emitted intent must be the same account as s. Test: run validateAddress + createWithdrawalIntents on `ltc1pqar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq2ka6yp` and inspect the emitted memo/recipient/receiver.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: call `validateAddress('ltc1pqar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq2ka6yp', Chains.Litecoin)`; then `createWithdrawalIntents` with mocked fee and assert the encoded destination byte-for-byte; compare against the poa bridge's documented accepted format.
