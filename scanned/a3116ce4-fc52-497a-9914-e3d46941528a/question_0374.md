# Q0374: Bitcoin bech32 with trailing newline via OmniBridge (createWithdrawalIntents)

## Question
Using `IntentsSDK.createWithdrawalIntents` for `Bitcoin`, can `bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq\n` (bech32 with trailing newline) pass `validateBtcAddress` and reach `deriveOmniWithdrawIntentParams` -> `ft_withdraw` to `omni.bridge.near` with `msg.recipient = omniAddress(chainKind, address)` so that the destination on chain is not the one validated, given that if the decoder trims, the untrimmed string goes into `WITHDRAW_TO:` memo?

## Target
- File/function: packages/intents-sdk/src/lib/validateAddress.ts `validateBtcAddress`; packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts `validateWithdrawal` / `createWithdrawalIntents`
- Entrypoint: `IntentsSDK.createWithdrawalIntents` (returns raw `IntentPrimitive[]` for the integrator to sign with any signer)
- Attacker controls: `destinationAddress` string (`bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq\n`), `assetId` for a Bitcoin omni token, `destinationMemo`
- Exploit idea: if the decoder trims, the untrimmed string goes into `WITHDRAW_TO:` memo. Encoding path: `deriveOmniWithdrawIntentParams` -> `ft_withdraw` to `omni.bridge.near` with `msg.recipient = omniAddress(chainKind, address)`.
- Invariant to test: For every string s where `validateAddress(s, 'bip122:000000000019d6689c085ae165831e93')` is true, the payout address derived by the Omni Bridge connector on the destination chain from the emitted intent must be the same account as s. Test: run validateAddress + createWithdrawalIntents on `bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq\n` and inspect the emitted memo/recipient/receiver.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: call `validateAddress('bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq\n', Chains.Bitcoin)`; then `createWithdrawalIntents` with mocked fee and assert the encoded destination byte-for-byte; compare against the omni bridge's documented accepted format.
