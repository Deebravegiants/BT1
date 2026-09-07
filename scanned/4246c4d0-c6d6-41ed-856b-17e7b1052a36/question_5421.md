# Q5421: Sui uppercase hex via PoaBridge (estimateWithdrawalFee)

## Question
Using `IntentsSDK.estimateWithdrawalFee` with `amount: 0n, feeInclusive: false` for `Sui`, can `0x2F1E0D9D0B3C5A6B7C8D9E0F1A2B3C4D5E6F708192A3B4C5D6E7F8091A2B3C4D` (uppercase hex) pass `validateSuiAddress` and reach `createWithdrawIntentPrimitive` -> `ft_withdraw` to the `omft.near` token with memo `WITHDRAW_TO:<address>[:<memo>]` so that the destination on chain is not the one validated, given that case-insensitive regex; `compareAddresses` normalises but memo does not?

## Target
- File/function: packages/intents-sdk/src/lib/validateAddress.ts `validateSuiAddress`; packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts `validateWithdrawal` / `createWithdrawalIntents`
- Entrypoint: `IntentsSDK.estimateWithdrawalFee` with `amount: 0n, feeInclusive: false` (sets `skipMinAmountValidation` and still runs `validateWithdrawal`)
- Attacker controls: `destinationAddress` string (`0x2F1E0D9D0B3C5A6B7C8D9E0F1A2B3C4D5E6F708192A3B4C5D6E7F8091A2B3C4D`), `assetId` for a Sui poa token, `destinationMemo`
- Exploit idea: case-insensitive regex; `compareAddresses` normalises but memo does not. Encoding path: `createWithdrawIntentPrimitive` -> `ft_withdraw` to the `omft.near` token with memo `WITHDRAW_TO:<address>[:<memo>]`.
- Invariant to test: For every string s where `validateAddress(s, 'sui:mainnet')` is true, the payout address derived by the PoA bridge relayer (bridge.chaindefuser.com) from the emitted intent must be the same account as s. Test: run validateAddress + createWithdrawalIntents on `0x2F1E0D9D0B3C5A6B7C8D9E0F1A2B3C4D5E6F708192A3B4C5D6E7F8091A2B3C4D` and inspect the emitted memo/recipient/receiver.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: call `validateAddress('0x2F1E0D9D0B3C5A6B7C8D9E0F1A2B3C4D5E6F708192A3B4C5D6E7F8091A2B3C4D', Chains.Sui)`; then `createWithdrawalIntents` with mocked fee and assert the encoded destination byte-for-byte; compare against the poa bridge's documented accepted format.
