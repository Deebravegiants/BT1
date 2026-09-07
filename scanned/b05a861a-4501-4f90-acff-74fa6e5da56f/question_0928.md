# Q0928: Litecoin all-uppercase ltc1 bech32 via PoaBridge (createWithdrawalIntents)

## Question
Using `IntentsSDK.createWithdrawalIntents` for `Litecoin`, can `LTC1QMYR5QY5S0VQ8F0M3Q7Q2C8ZJ3SD6L4MX4V7RYJ` (all-uppercase ltc1 bech32) pass `validateLitecoinAddress` and reach `createWithdrawIntentPrimitive` -> `ft_withdraw` to the `omft.near` token with memo `WITHDRAW_TO:<address>[:<memo>]` so that the destination on chain is not the one validated, given that prefix check lowercases, decode accepts uppercase; memo gets uppercase?

## Target
- File/function: packages/intents-sdk/src/lib/validateAddress.ts `validateLitecoinAddress`; packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts `validateWithdrawal` / `createWithdrawalIntents`
- Entrypoint: `IntentsSDK.createWithdrawalIntents` (returns raw `IntentPrimitive[]` for the integrator to sign with any signer)
- Attacker controls: `destinationAddress` string (`LTC1QMYR5QY5S0VQ8F0M3Q7Q2C8ZJ3SD6L4MX4V7RYJ`), `assetId` for a Litecoin poa token, `destinationMemo`
- Exploit idea: prefix check lowercases, decode accepts uppercase; memo gets uppercase. Encoding path: `createWithdrawIntentPrimitive` -> `ft_withdraw` to the `omft.near` token with memo `WITHDRAW_TO:<address>[:<memo>]`.
- Invariant to test: For every string s where `validateAddress(s, 'bip122:12a765e31ffd4059bada1e25190f6e98')` is true, the payout address derived by the PoA bridge relayer (bridge.chaindefuser.com) from the emitted intent must be the same account as s. Test: run validateAddress + createWithdrawalIntents on `LTC1QMYR5QY5S0VQ8F0M3Q7Q2C8ZJ3SD6L4MX4V7RYJ` and inspect the emitted memo/recipient/receiver.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: call `validateAddress('LTC1QMYR5QY5S0VQ8F0M3Q7Q2C8ZJ3SD6L4MX4V7RYJ', Chains.Litecoin)`; then `createWithdrawalIntents` with mocked fee and assert the encoded destination byte-for-byte; compare against the poa bridge's documented accepted format.
