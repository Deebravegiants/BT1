# Q0022: Bitcoin all-uppercase bech32 via PoaBridge (estimateWithdrawalFee)

## Question
Can an unprivileged user enter through `IntentsSDK.estimateWithdrawalFee` with `amount: 0n, feeInclusive: false` on the PoaBridge route for Bitcoin with `destinationAddress` = `BC1QAR0SRRR7XFKVY5L643LYDNW9RE59GTZZWF5MDQ` (all-uppercase bech32) and make `validateAddress` (`validateBtcAddress`) accept a string that `createWithdrawIntentPrimitive` -> `ft_withdraw` to the `omft.near` token with memo `WITHDRAW_TO:<address>[:<memo>]` then forwards unchanged, so the address the PoA bridge relayer (bridge.chaindefuser.com) pays differs from the account the user controls and the withdrawal is lost?

## Target
- File/function: packages/intents-sdk/src/lib/validateAddress.ts `validateBtcAddress`; packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts `validateWithdrawal` / `createWithdrawalIntents`
- Entrypoint: `IntentsSDK.estimateWithdrawalFee` with `amount: 0n, feeInclusive: false` (sets `skipMinAmountValidation` and still runs `validateWithdrawal`)
- Attacker controls: `destinationAddress` string (`BC1QAR0SRRR7XFKVY5L643LYDNW9RE59GTZZWF5MDQ`), `assetId` for a Bitcoin poa token, `destinationMemo`
- Exploit idea: `validateBtcBech32Address` lowercases only the prefix check; bech32 decode accepts all-uppercase, so the raw uppercase string reaches the PoA memo and Omni `recipient` untouched. Encoding path: `createWithdrawIntentPrimitive` -> `ft_withdraw` to the `omft.near` token with memo `WITHDRAW_TO:<address>[:<memo>]`.
- Invariant to test: For every string s where `validateAddress(s, 'bip122:000000000019d6689c085ae165831e93')` is true, the payout address derived by the PoA bridge relayer (bridge.chaindefuser.com) from the emitted intent must be the same account as s. Test: run validateAddress + createWithdrawalIntents on `BC1QAR0SRRR7XFKVY5L643LYDNW9RE59GTZZWF5MDQ` and inspect the emitted memo/recipient/receiver.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: call `validateAddress('BC1QAR0SRRR7XFKVY5L643LYDNW9RE59GTZZWF5MDQ', Chains.Bitcoin)`; then `createWithdrawalIntents` with mocked fee and assert the encoded destination byte-for-byte; compare against the poa bridge's documented accepted format.
