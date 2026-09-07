# Q4849: Fogo Solana-shaped address on Fogo route via OmniBridge (signAndSendWithdrawalIntent)

## Question
Can an unprivileged user enter through `IntentsSDK.signAndSendWithdrawalIntent` with a caller-supplied `feeEstimation` on the OmniBridge route for Fogo with `destinationAddress` = `EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v` (Solana-shaped address on Fogo route) and make `validateAddress` (`validateSolAddress`) accept a string that `deriveOmniWithdrawIntentParams` -> `ft_withdraw` to `omni.bridge.near` with `msg.recipient = omniAddress(chainKind, address)` then forwards unchanged, so the address the Omni Bridge connector on the destination chain pays differs from the account the user controls and the withdrawal is lost?

## Target
- File/function: packages/intents-sdk/src/lib/validateAddress.ts `validateSolAddress`; packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts `validateWithdrawal` / `createWithdrawalIntents`
- Entrypoint: `IntentsSDK.signAndSendWithdrawalIntent` with a caller-supplied `feeEstimation` (skips `_estimateWithdrawalFee`'s `FeeExceedsAmountError` and re-validates only inside `createWithdrawalIntents`)
- Attacker controls: `destinationAddress` string (`EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v`), `assetId` for a Fogo omni token, `destinationMemo`
- Exploit idea: Fogo shares `validateSolAddress`; a Solana account with no Fogo counterpart passes. Encoding path: `deriveOmniWithdrawIntentParams` -> `ft_withdraw` to `omni.bridge.near` with `msg.recipient = omniAddress(chainKind, address)`.
- Invariant to test: For every string s where `validateAddress(s, 'solana:CDLtwKnaCoK157uaHQDj4fHu72AyD251')` is true, the payout address derived by the Omni Bridge connector on the destination chain from the emitted intent must be the same account as s. Test: run validateAddress + createWithdrawalIntents on `EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v` and inspect the emitted memo/recipient/receiver.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: call `validateAddress('EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', Chains.Fogo)`; then `createWithdrawalIntents` with mocked fee and assert the encoded destination byte-for-byte; compare against the omni bridge's documented accepted format.
