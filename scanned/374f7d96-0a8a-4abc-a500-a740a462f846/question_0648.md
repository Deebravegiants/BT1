# Q0648: Zcash TEX address via OmniBridge (estimateWithdrawalFee)

## Question
Can an unprivileged user enter through `IntentsSDK.estimateWithdrawalFee` with `amount: 0n, feeInclusive: false` on the OmniBridge route for Zcash with `destinationAddress` = `tex1s2rt77ggv6q989lr49rkgzmh5slsksa9khdgte` (TEX address) and make `validateAddress` (`validateZcashAddress`) accept a string that `deriveOmniWithdrawIntentParams` -> `ft_withdraw` to `omni.bridge.near` with `msg.recipient = omniAddress(chainKind, address)` then forwards unchanged, so the address the Omni Bridge connector on the destination chain pays differs from the account the user controls and the withdrawal is lost?

## Target
- File/function: packages/intents-sdk/src/lib/validateAddress.ts `validateZcashAddress`; packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts `validateWithdrawal` / `createWithdrawalIntents`
- Entrypoint: `IntentsSDK.estimateWithdrawalFee` with `amount: 0n, feeInclusive: false` (sets `skipMinAmountValidation` and still runs `validateWithdrawal`)
- Attacker controls: `destinationAddress` string (`tex1s2rt77ggv6q989lr49rkgzmh5slsksa9khdgte`), `assetId` for a Zcash omni token, `destinationMemo`
- Exploit idea: accepted when 20 bytes; confirm Omni Zcash connector supports TEX outputs. Encoding path: `deriveOmniWithdrawIntentParams` -> `ft_withdraw` to `omni.bridge.near` with `msg.recipient = omniAddress(chainKind, address)`.
- Invariant to test: For every string s where `validateAddress(s, 'bip122:00040fe8ec8471911baa1db1266ea15d')` is true, the payout address derived by the Omni Bridge connector on the destination chain from the emitted intent must be the same account as s. Test: run validateAddress + createWithdrawalIntents on `tex1s2rt77ggv6q989lr49rkgzmh5slsksa9khdgte` and inspect the emitted memo/recipient/receiver.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: call `validateAddress('tex1s2rt77ggv6q989lr49rkgzmh5slsksa9khdgte', Chains.Zcash)`; then `createWithdrawalIntents` with mocked fee and assert the encoded destination byte-for-byte; compare against the omni bridge's documented accepted format.
