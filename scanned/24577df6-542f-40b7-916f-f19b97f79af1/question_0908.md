# Q0908: Litecoin legacy L address bad checksum via PoaBridge (estimateWithdrawalFee)

## Question
If a counterparty supplies `destinationAddress` = `LM2WMpR1Rp6j3Sa59cMXMs1SPzj9eXpGc2` (legacy L address bad checksum) for a Litecoin withdrawal via `IntentsSDK.estimateWithdrawalFee` with `amount: 0n, feeInclusive: false`, does `validateLitecoinAddress` return true while `createWithdrawIntentPrimitive` -> `ft_withdraw` to the `omft.near` token with memo `WITHDRAW_TO:<address>[:<memo>]` encodes a value the PoA bridge relayer (bridge.chaindefuser.com) interprets differently, breaking address-validated == address-paid?

## Target
- File/function: packages/intents-sdk/src/lib/validateAddress.ts `validateLitecoinAddress`; packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts `validateWithdrawal` / `createWithdrawalIntents`
- Entrypoint: `IntentsSDK.estimateWithdrawalFee` with `amount: 0n, feeInclusive: false` (sets `skipMinAmountValidation` and still runs `validateWithdrawal`)
- Attacker controls: `destinationAddress` string (`LM2WMpR1Rp6j3Sa59cMXMs1SPzj9eXpGc2`), `assetId` for a Litecoin poa token, `destinationMemo`
- Exploit idea: Base58Check is verified here; confirm the shared-prefix branch for '3' is the only gap. Encoding path: `createWithdrawIntentPrimitive` -> `ft_withdraw` to the `omft.near` token with memo `WITHDRAW_TO:<address>[:<memo>]`.
- Invariant to test: For every string s where `validateAddress(s, 'bip122:12a765e31ffd4059bada1e25190f6e98')` is true, the payout address derived by the PoA bridge relayer (bridge.chaindefuser.com) from the emitted intent must be the same account as s. Test: run validateAddress + createWithdrawalIntents on `LM2WMpR1Rp6j3Sa59cMXMs1SPzj9eXpGc2` and inspect the emitted memo/recipient/receiver.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: call `validateAddress('LM2WMpR1Rp6j3Sa59cMXMs1SPzj9eXpGc2', Chains.Litecoin)`; then `createWithdrawalIntents` with mocked fee and assert the encoded destination byte-for-byte; compare against the poa bridge's documented accepted format.
