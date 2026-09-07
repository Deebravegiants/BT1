# Q0516: BitcoinCash CashAddr with bchtest: prefix via PoaBridge (estimateWithdrawalFee)

## Question
If a counterparty supplies `destinationAddress` = `bchtest:qpm2qsznhks23z7629mms6s4cwef74vcwvy22gdx6a` (CashAddr with bchtest: prefix) for a BitcoinCash withdrawal via `IntentsSDK.estimateWithdrawalFee` with `amount: 0n, feeInclusive: false`, does `validateBchAddress` return true while `createWithdrawIntentPrimitive` -> `ft_withdraw` to the `omft.near` token with memo `WITHDRAW_TO:<address>[:<memo>]` encodes a value the PoA bridge relayer (bridge.chaindefuser.com) interprets differently, breaking address-validated == address-paid?

## Target
- File/function: packages/intents-sdk/src/lib/validateAddress.ts `validateBchAddress`; packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts `validateWithdrawal` / `createWithdrawalIntents`
- Entrypoint: `IntentsSDK.estimateWithdrawalFee` with `amount: 0n, feeInclusive: false` (sets `skipMinAmountValidation` and still runs `validateWithdrawal`)
- Attacker controls: `destinationAddress` string (`bchtest:qpm2qsznhks23z7629mms6s4cwef74vcwvy22gdx6a`), `assetId` for a BitcoinCash poa token, `destinationMemo`
- Exploit idea: prefix check happens after lowercasing; confirm testnet prefix is rejected and not silently rewritten. Encoding path: `createWithdrawIntentPrimitive` -> `ft_withdraw` to the `omft.near` token with memo `WITHDRAW_TO:<address>[:<memo>]`.
- Invariant to test: For every string s where `validateAddress(s, 'bip122:000000000000000000651ef99cb9fcbe')` is true, the payout address derived by the PoA bridge relayer (bridge.chaindefuser.com) from the emitted intent must be the same account as s. Test: run validateAddress + createWithdrawalIntents on `bchtest:qpm2qsznhks23z7629mms6s4cwef74vcwvy22gdx6a` and inspect the emitted memo/recipient/receiver.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: call `validateAddress('bchtest:qpm2qsznhks23z7629mms6s4cwef74vcwvy22gdx6a', Chains.BitcoinCash)`; then `createWithdrawalIntents` with mocked fee and assert the encoded destination byte-for-byte; compare against the poa bridge's documented accepted format.
