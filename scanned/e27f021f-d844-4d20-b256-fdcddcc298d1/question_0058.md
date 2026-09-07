# Q0058: Bitcoin all-uppercase bech32 via OmniBridge (estimateWithdrawalFee)

## Question
Using `IntentsSDK.estimateWithdrawalFee` with `amount: 0n, feeInclusive: false` for `Bitcoin`, can `BC1QAR0SRRR7XFKVY5L643LYDNW9RE59GTZZWF5MDQ` (all-uppercase bech32) pass `validateBtcAddress` and reach `deriveOmniWithdrawIntentParams` -> `ft_withdraw` to `omni.bridge.near` with `msg.recipient = omniAddress(chainKind, address)` so that the destination on chain is not the one validated, given that `validateBtcBech32Address` lowercases only the prefix check; bech32 decode accepts all-uppercase, so the raw uppercase string reaches the PoA memo and Omni `recipient` untouched?

## Target
- File/function: packages/intents-sdk/src/lib/validateAddress.ts `validateBtcAddress`; packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts `validateWithdrawal` / `createWithdrawalIntents`
- Entrypoint: `IntentsSDK.estimateWithdrawalFee` with `amount: 0n, feeInclusive: false` (sets `skipMinAmountValidation` and still runs `validateWithdrawal`)
- Attacker controls: `destinationAddress` string (`BC1QAR0SRRR7XFKVY5L643LYDNW9RE59GTZZWF5MDQ`), `assetId` for a Bitcoin omni token, `destinationMemo`
- Exploit idea: `validateBtcBech32Address` lowercases only the prefix check; bech32 decode accepts all-uppercase, so the raw uppercase string reaches the PoA memo and Omni `recipient` untouched. Encoding path: `deriveOmniWithdrawIntentParams` -> `ft_withdraw` to `omni.bridge.near` with `msg.recipient = omniAddress(chainKind, address)`.
- Invariant to test: For every string s where `validateAddress(s, 'bip122:000000000019d6689c085ae165831e93')` is true, the payout address derived by the Omni Bridge connector on the destination chain from the emitted intent must be the same account as s. Test: run validateAddress + createWithdrawalIntents on `BC1QAR0SRRR7XFKVY5L643LYDNW9RE59GTZZWF5MDQ` and inspect the emitted memo/recipient/receiver.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: call `validateAddress('BC1QAR0SRRR7XFKVY5L643LYDNW9RE59GTZZWF5MDQ', Chains.Bitcoin)`; then `createWithdrawalIntents` with mocked fee and assert the encoded destination byte-for-byte; compare against the omni bridge's documented accepted format.
