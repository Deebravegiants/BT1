# Q4980: Tron base58 T address with bad checksum via PoaBridge (signAndSendWithdrawalIntent)

## Question
Using `IntentsSDK.signAndSendWithdrawalIntent` with a caller-supplied `feeEstimation` for `Tron`, can `TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6u` (base58 T address with bad checksum) pass `validateTronAddress` and reach `createWithdrawIntentPrimitive` -> `ft_withdraw` to the `omft.near` token with memo `WITHDRAW_TO:<address>[:<memo>]` so that the destination on chain is not the one validated, given that checksum verified in validator, but `tronAddressToHex` used for identity does not verify it?

## Target
- File/function: packages/intents-sdk/src/lib/validateAddress.ts `validateTronAddress`; packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts `validateWithdrawal` / `createWithdrawalIntents`
- Entrypoint: `IntentsSDK.signAndSendWithdrawalIntent` with a caller-supplied `feeEstimation` (skips `_estimateWithdrawalFee`'s `FeeExceedsAmountError` and re-validates only inside `createWithdrawalIntents`)
- Attacker controls: `destinationAddress` string (`TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6u`), `assetId` for a Tron poa token, `destinationMemo`
- Exploit idea: checksum verified in validator, but `tronAddressToHex` used for identity does not verify it. Encoding path: `createWithdrawIntentPrimitive` -> `ft_withdraw` to the `omft.near` token with memo `WITHDRAW_TO:<address>[:<memo>]`.
- Invariant to test: For every string s where `validateAddress(s, 'tron:27Lqcw')` is true, the payout address derived by the PoA bridge relayer (bridge.chaindefuser.com) from the emitted intent must be the same account as s. Test: run validateAddress + createWithdrawalIntents on `TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6u` and inspect the emitted memo/recipient/receiver.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: call `validateAddress('TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6u', Chains.Tron)`; then `createWithdrawalIntents` with mocked fee and assert the encoded destination byte-for-byte; compare against the poa bridge's documented accepted format.
