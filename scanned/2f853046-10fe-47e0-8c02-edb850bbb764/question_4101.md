# Q4101: Plasma the bridged token's own contract on destination via PoaBridge (signAndSendWithdrawalIntent)

## Question
Can an unprivileged user enter through `IntentsSDK.signAndSendWithdrawalIntent` with a caller-supplied `feeEstimation` on the PoaBridge route for Plasma with `destinationAddress` = `<token contract on chain>` (the bridged token's own contract on destination) and make `validateAddress` (`validateEthAddress`) accept a string that `createWithdrawIntentPrimitive` -> `ft_withdraw` to the `omft.near` token with memo `WITHDRAW_TO:<address>[:<memo>]` then forwards unchanged, so the address the PoA bridge relayer (bridge.chaindefuser.com) pays differs from the account the user controls and the withdrawal is lost?

## Target
- File/function: packages/intents-sdk/src/lib/validateAddress.ts `validateEthAddress`; packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts `validateWithdrawal` / `createWithdrawalIntents`
- Entrypoint: `IntentsSDK.signAndSendWithdrawalIntent` with a caller-supplied `feeEstimation` (skips `_estimateWithdrawalFee`'s `FeeExceedsAmountError` and re-validates only inside `createWithdrawalIntents`)
- Attacker controls: `destinationAddress` string (`<token contract on chain>`), `assetId` for a Plasma poa token, `destinationMemo`
- Exploit idea: `DestinationAddressMatchesTokenAddressError` relies on `origin_chain_address` / `getAddress(destTokenOmniAddress)`; a proxy or wrapper address passes. Encoding path: `createWithdrawIntentPrimitive` -> `ft_withdraw` to the `omft.near` token with memo `WITHDRAW_TO:<address>[:<memo>]`.
- Invariant to test: For every string s where `validateAddress(s, 'eip155:9745')` is true, the payout address derived by the PoA bridge relayer (bridge.chaindefuser.com) from the emitted intent must be the same account as s. Test: run validateAddress + createWithdrawalIntents on `<token contract on chain>` and inspect the emitted memo/recipient/receiver.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: call `validateAddress('<token contract on chain>', Chains.Plasma)`; then `createWithdrawalIntents` with mocked fee and assert the encoded destination byte-for-byte; compare against the poa bridge's documented accepted format.
