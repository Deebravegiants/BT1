# Q0629: Zcash TEX address via OmniBridge (signAndSendWithdrawalIntent)

## Question
If a counterparty supplies `destinationAddress` = `tex1s2rt77ggv6q989lr49rkgzmh5slsksa9khdgte` (TEX address) for a Zcash withdrawal via `IntentsSDK.signAndSendWithdrawalIntent` with a caller-supplied `feeEstimation`, does `validateZcashAddress` return true while `deriveOmniWithdrawIntentParams` -> `ft_withdraw` to `omni.bridge.near` with `msg.recipient = omniAddress(chainKind, address)` encodes a value the Omni Bridge connector on the destination chain interprets differently, breaking address-validated == address-paid?

## Target
- File/function: packages/intents-sdk/src/lib/validateAddress.ts `validateZcashAddress`; packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts `validateWithdrawal` / `createWithdrawalIntents`
- Entrypoint: `IntentsSDK.signAndSendWithdrawalIntent` with a caller-supplied `feeEstimation` (skips `_estimateWithdrawalFee`'s `FeeExceedsAmountError` and re-validates only inside `createWithdrawalIntents`)
- Attacker controls: `destinationAddress` string (`tex1s2rt77ggv6q989lr49rkgzmh5slsksa9khdgte`), `assetId` for a Zcash omni token, `destinationMemo`
- Exploit idea: accepted when 20 bytes; confirm Omni Zcash connector supports TEX outputs. Encoding path: `deriveOmniWithdrawIntentParams` -> `ft_withdraw` to `omni.bridge.near` with `msg.recipient = omniAddress(chainKind, address)`.
- Invariant to test: For every string s where `validateAddress(s, 'bip122:00040fe8ec8471911baa1db1266ea15d')` is true, the payout address derived by the Omni Bridge connector on the destination chain from the emitted intent must be the same account as s. Test: run validateAddress + createWithdrawalIntents on `tex1s2rt77ggv6q989lr49rkgzmh5slsksa9khdgte` and inspect the emitted memo/recipient/receiver.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: call `validateAddress('tex1s2rt77ggv6q989lr49rkgzmh5slsksa9khdgte', Chains.Zcash)`; then `createWithdrawalIntents` with mocked fee and assert the encoded destination byte-for-byte; compare against the omni bridge's documented accepted format.
