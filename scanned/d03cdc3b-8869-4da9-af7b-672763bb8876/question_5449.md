# Q5449: Sui object id of a coin instead of an account via PoaBridge (estimateWithdrawalFee)

## Question
If a counterparty supplies `destinationAddress` = `0x0000000000000000000000000000000000000000000000000000000000000002` (object id of a coin instead of an account) for a Sui withdrawal via `IntentsSDK.estimateWithdrawalFee` with `amount: 0n, feeInclusive: false`, does `validateSuiAddress` return true while `createWithdrawIntentPrimitive` -> `ft_withdraw` to the `omft.near` token with memo `WITHDRAW_TO:<address>[:<memo>]` encodes a value the PoA bridge relayer (bridge.chaindefuser.com) interprets differently, breaking address-validated == address-paid?

## Target
- File/function: packages/intents-sdk/src/lib/validateAddress.ts `validateSuiAddress`; packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts `validateWithdrawal` / `createWithdrawalIntents`
- Entrypoint: `IntentsSDK.estimateWithdrawalFee` with `amount: 0n, feeInclusive: false` (sets `skipMinAmountValidation` and still runs `validateWithdrawal`)
- Attacker controls: `destinationAddress` string (`0x0000000000000000000000000000000000000000000000000000000000000002`), `assetId` for a Sui poa token, `destinationMemo`
- Exploit idea: any 32-byte hex passes; Sui framework object ids are not accounts. Encoding path: `createWithdrawIntentPrimitive` -> `ft_withdraw` to the `omft.near` token with memo `WITHDRAW_TO:<address>[:<memo>]`.
- Invariant to test: For every string s where `validateAddress(s, 'sui:mainnet')` is true, the payout address derived by the PoA bridge relayer (bridge.chaindefuser.com) from the emitted intent must be the same account as s. Test: run validateAddress + createWithdrawalIntents on `0x0000000000000000000000000000000000000000000000000000000000000002` and inspect the emitted memo/recipient/receiver.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: call `validateAddress('0x0000000000000000000000000000000000000000000000000000000000000002', Chains.Sui)`; then `createWithdrawalIntents` with mocked fee and assert the encoded destination byte-for-byte; compare against the poa bridge's documented accepted format.
