# Q1700: BNB the bridged token's own contract on destination via OmniBridge (signAndSendWithdrawalIntent)

## Question
Can an unprivileged user enter through `IntentsSDK.signAndSendWithdrawalIntent` with a caller-supplied `feeEstimation` on the OmniBridge route for BNB with `destinationAddress` = `<token contract on chain>` (the bridged token's own contract on destination) and make `validateAddress` (`validateEthAddress`) accept a string that `deriveOmniWithdrawIntentParams` -> `ft_withdraw` to `omni.bridge.near` with `msg.recipient = omniAddress(chainKind, address)` then forwards unchanged, so the address the Omni Bridge connector on the destination chain pays differs from the account the user controls and the withdrawal is lost?

## Target
- File/function: packages/intents-sdk/src/lib/validateAddress.ts `validateEthAddress`; packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts `validateWithdrawal` / `createWithdrawalIntents`
- Entrypoint: `IntentsSDK.signAndSendWithdrawalIntent` with a caller-supplied `feeEstimation` (skips `_estimateWithdrawalFee`'s `FeeExceedsAmountError` and re-validates only inside `createWithdrawalIntents`)
- Attacker controls: `destinationAddress` string (`<token contract on chain>`), `assetId` for a BNB omni token, `destinationMemo`
- Exploit idea: `DestinationAddressMatchesTokenAddressError` relies on `origin_chain_address` / `getAddress(destTokenOmniAddress)`; a proxy or wrapper address passes. Encoding path: `deriveOmniWithdrawIntentParams` -> `ft_withdraw` to `omni.bridge.near` with `msg.recipient = omniAddress(chainKind, address)`.
- Invariant to test: For every string s where `validateAddress(s, 'eip155:56')` is true, the payout address derived by the Omni Bridge connector on the destination chain from the emitted intent must be the same account as s. Test: run validateAddress + createWithdrawalIntents on `<token contract on chain>` and inspect the emitted memo/recipient/receiver.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: call `validateAddress('<token contract on chain>', Chains.BNB)`; then `createWithdrawalIntents` with mocked fee and assert the encoded destination byte-for-byte; compare against the omni bridge's documented accepted format.
