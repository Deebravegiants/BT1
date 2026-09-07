# Q0233: Bitcoin P2SH 3... address via OmniBridge (processWithdrawal)

## Question
Using `IntentsSDK.processWithdrawal` for `Bitcoin`, can `3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy` (P2SH 3... address) pass `validateBtcAddress` and reach `deriveOmniWithdrawIntentParams` -> `ft_withdraw` to `omni.bridge.near` with `msg.recipient = omniAddress(chainKind, address)` so that the destination on chain is not the one validated, given that valid on Bitcoin and Litecoin; `validateLitecoinAddress` also accepts it, so a Litecoin-route call cannot tell them apart?

## Target
- File/function: packages/intents-sdk/src/lib/validateAddress.ts `validateBtcAddress`; packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts `validateWithdrawal` / `createWithdrawalIntents`
- Entrypoint: `IntentsSDK.processWithdrawal` (end-to-end: estimate -> validate -> sign -> publish -> wait)
- Attacker controls: `destinationAddress` string (`3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy`), `assetId` for a Bitcoin omni token, `destinationMemo`
- Exploit idea: valid on Bitcoin and Litecoin; `validateLitecoinAddress` also accepts it, so a Litecoin-route call cannot tell them apart. Encoding path: `deriveOmniWithdrawIntentParams` -> `ft_withdraw` to `omni.bridge.near` with `msg.recipient = omniAddress(chainKind, address)`.
- Invariant to test: For every string s where `validateAddress(s, 'bip122:000000000019d6689c085ae165831e93')` is true, the payout address derived by the Omni Bridge connector on the destination chain from the emitted intent must be the same account as s. Test: run validateAddress + createWithdrawalIntents on `3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy` and inspect the emitted memo/recipient/receiver.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: call `validateAddress('3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy', Chains.Bitcoin)`; then `createWithdrawalIntents` with mocked fee and assert the encoded destination byte-for-byte; compare against the omni bridge's documented accepted format.
