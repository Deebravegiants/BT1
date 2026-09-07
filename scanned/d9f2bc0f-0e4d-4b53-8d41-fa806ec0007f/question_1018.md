# Q1018: Ethereum checksum-cased address with wrong checksum via OmniBridge (signAndSendWithdrawalIntent)

## Question
Using `IntentsSDK.signAndSendWithdrawalIntent` with a caller-supplied `feeEstimation` for `Ethereum`, can `0xdAC17F958D2ee523a2206206994597C13D831ec8` (checksum-cased address with wrong checksum) pass `validateEthAddress` and reach `deriveOmniWithdrawIntentParams` -> `ft_withdraw` to `omni.bridge.near` with `msg.recipient = omniAddress(chainKind, address)` so that the destination on chain is not the one validated, given that `isAddress(strict:true)` rejects bad EIP-55 checksums; confirm all-lowercase bypass is intended and that the bridge receives lowercase?

## Target
- File/function: packages/intents-sdk/src/lib/validateAddress.ts `validateEthAddress`; packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts `validateWithdrawal` / `createWithdrawalIntents`
- Entrypoint: `IntentsSDK.signAndSendWithdrawalIntent` with a caller-supplied `feeEstimation` (skips `_estimateWithdrawalFee`'s `FeeExceedsAmountError` and re-validates only inside `createWithdrawalIntents`)
- Attacker controls: `destinationAddress` string (`0xdAC17F958D2ee523a2206206994597C13D831ec8`), `assetId` for a Ethereum omni token, `destinationMemo`
- Exploit idea: `isAddress(strict:true)` rejects bad EIP-55 checksums; confirm all-lowercase bypass is intended and that the bridge receives lowercase. Encoding path: `deriveOmniWithdrawIntentParams` -> `ft_withdraw` to `omni.bridge.near` with `msg.recipient = omniAddress(chainKind, address)`.
- Invariant to test: For every string s where `validateAddress(s, 'eip155:1')` is true, the payout address derived by the Omni Bridge connector on the destination chain from the emitted intent must be the same account as s. Test: run validateAddress + createWithdrawalIntents on `0xdAC17F958D2ee523a2206206994597C13D831ec8` and inspect the emitted memo/recipient/receiver.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: call `validateAddress('0xdAC17F958D2ee523a2206206994597C13D831ec8', Chains.Ethereum)`; then `createWithdrawalIntents` with mocked fee and assert the encoded destination byte-for-byte; compare against the omni bridge's documented accepted format.
