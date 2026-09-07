# Q5082: XRPL classic address with requireDestinationTag and empty memo via PoaBridge (signAndSendWithdrawalIntent)

## Question
If a counterparty supplies `destinationAddress` = `rEb8TK3gBgk5auZkwc6sHnwrGVJH8DuaLh` (classic address with requireDestinationTag and empty memo) for a XRPL withdrawal via `IntentsSDK.signAndSendWithdrawalIntent` with a caller-supplied `feeEstimation`, does `validateXrpAddress` return true while `createWithdrawIntentPrimitive` -> `ft_withdraw` to the `omft.near` token with memo `WITHDRAW_TO:<address>[:<memo>]` encodes a value the PoA bridge relayer (bridge.chaindefuser.com) interprets differently, breaking address-validated == address-paid?

## Target
- File/function: packages/intents-sdk/src/lib/validateAddress.ts `validateXrpAddress`; packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts `validateWithdrawal` / `createWithdrawalIntents`
- Entrypoint: `IntentsSDK.signAndSendWithdrawalIntent` with a caller-supplied `feeEstimation` (skips `_estimateWithdrawalFee`'s `FeeExceedsAmountError` and re-validates only inside `createWithdrawalIntents`)
- Attacker controls: `destinationAddress` string (`rEb8TK3gBgk5auZkwc6sHnwrGVJH8DuaLh`), `assetId` for a XRPL poa token, `destinationMemo`
- Exploit idea: `XrplDestinationTagRequiredError` only when `account_flags.requireDestinationTag`; check `!args.destinationMemo` vs `''` vs `'0'`. Encoding path: `createWithdrawIntentPrimitive` -> `ft_withdraw` to the `omft.near` token with memo `WITHDRAW_TO:<address>[:<memo>]`.
- Invariant to test: For every string s where `validateAddress(s, 'xrpl:0')` is true, the payout address derived by the PoA bridge relayer (bridge.chaindefuser.com) from the emitted intent must be the same account as s. Test: run validateAddress + createWithdrawalIntents on `rEb8TK3gBgk5auZkwc6sHnwrGVJH8DuaLh` and inspect the emitted memo/recipient/receiver.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: call `validateAddress('rEb8TK3gBgk5auZkwc6sHnwrGVJH8DuaLh', Chains.XRPL)`; then `createWithdrawalIntents` with mocked fee and assert the encoded destination byte-for-byte; compare against the poa bridge's documented accepted format.
