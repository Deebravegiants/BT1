# Q1118: Ethereum 0x000...dead in mixed case via PoaBridge (signAndSendWithdrawalIntent)

## Question
If a counterparty supplies `destinationAddress` = `0x000000000000000000000000000000000000dEaD` (0x000...dead in mixed case) for a Ethereum withdrawal via `IntentsSDK.signAndSendWithdrawalIntent` with a caller-supplied `feeEstimation`, does `validateEthAddress` return true while `createWithdrawIntentPrimitive` -> `ft_withdraw` to the `omft.near` token with memo `WITHDRAW_TO:<address>[:<memo>]` encodes a value the PoA bridge relayer (bridge.chaindefuser.com) interprets differently, breaking address-validated == address-paid?

## Target
- File/function: packages/intents-sdk/src/lib/validateAddress.ts `validateEthAddress`; packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts `validateWithdrawal` / `createWithdrawalIntents`
- Entrypoint: `IntentsSDK.signAndSendWithdrawalIntent` with a caller-supplied `feeEstimation` (skips `_estimateWithdrawalFee`'s `FeeExceedsAmountError` and re-validates only inside `createWithdrawalIntents`)
- Attacker controls: `destinationAddress` string (`0x000000000000000000000000000000000000dEaD`), `assetId` for a Ethereum poa token, `destinationMemo`
- Exploit idea: rejected via toLowerCase compare; check `0x0000000000000000000000000000000000000001` and precompiles pass. Encoding path: `createWithdrawIntentPrimitive` -> `ft_withdraw` to the `omft.near` token with memo `WITHDRAW_TO:<address>[:<memo>]`.
- Invariant to test: For every string s where `validateAddress(s, 'eip155:1')` is true, the payout address derived by the PoA bridge relayer (bridge.chaindefuser.com) from the emitted intent must be the same account as s. Test: run validateAddress + createWithdrawalIntents on `0x000000000000000000000000000000000000dEaD` and inspect the emitted memo/recipient/receiver.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: call `validateAddress('0x000000000000000000000000000000000000dEaD', Chains.Ethereum)`; then `createWithdrawalIntents` with mocked fee and assert the encoded destination byte-for-byte; compare against the poa bridge's documented accepted format.
