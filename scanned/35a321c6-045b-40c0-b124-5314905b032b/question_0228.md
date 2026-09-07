# Q0228: Bitcoin P2SH 3... address via PoaBridge (estimateWithdrawalFee)

## Question
If a counterparty supplies `destinationAddress` = `3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy` (P2SH 3... address) for a Bitcoin withdrawal via `IntentsSDK.estimateWithdrawalFee` with `amount: 0n, feeInclusive: false`, does `validateBtcAddress` return true while `createWithdrawIntentPrimitive` -> `ft_withdraw` to the `omft.near` token with memo `WITHDRAW_TO:<address>[:<memo>]` encodes a value the PoA bridge relayer (bridge.chaindefuser.com) interprets differently, breaking address-validated == address-paid?

## Target
- File/function: packages/intents-sdk/src/lib/validateAddress.ts `validateBtcAddress`; packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts `validateWithdrawal` / `createWithdrawalIntents`
- Entrypoint: `IntentsSDK.estimateWithdrawalFee` with `amount: 0n, feeInclusive: false` (sets `skipMinAmountValidation` and still runs `validateWithdrawal`)
- Attacker controls: `destinationAddress` string (`3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy`), `assetId` for a Bitcoin poa token, `destinationMemo`
- Exploit idea: valid on Bitcoin and Litecoin; `validateLitecoinAddress` also accepts it, so a Litecoin-route call cannot tell them apart. Encoding path: `createWithdrawIntentPrimitive` -> `ft_withdraw` to the `omft.near` token with memo `WITHDRAW_TO:<address>[:<memo>]`.
- Invariant to test: For every string s where `validateAddress(s, 'bip122:000000000019d6689c085ae165831e93')` is true, the payout address derived by the PoA bridge relayer (bridge.chaindefuser.com) from the emitted intent must be the same account as s. Test: run validateAddress + createWithdrawalIntents on `3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy` and inspect the emitted memo/recipient/receiver.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: call `validateAddress('3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy', Chains.Bitcoin)`; then `createWithdrawalIntents` with mocked fee and assert the encoded destination byte-for-byte; compare against the poa bridge's documented accepted format.
