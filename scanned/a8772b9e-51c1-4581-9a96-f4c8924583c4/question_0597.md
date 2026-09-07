# Q0597: Zcash transparent t1 with bad checksum via OmniBridge (signAndSendWithdrawalIntent)

## Question
Using `IntentsSDK.signAndSendWithdrawalIntent` with a caller-supplied `feeEstimation` for `Zcash`, can `t1XVXWCvpMgBvUaed4XDqWtgQgJSu1Ghz7G` (transparent t1 with bad checksum) pass `validateZcashAddress` and reach `deriveOmniWithdrawIntentParams` -> `ft_withdraw` to `omni.bridge.near` with `msg.recipient = omniAddress(chainKind, address)` so that the destination on chain is not the one validated, given that `validateZcashAddress` uses a regex for t1/t3 with no Base58Check?

## Target
- File/function: packages/intents-sdk/src/lib/validateAddress.ts `validateZcashAddress`; packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts `validateWithdrawal` / `createWithdrawalIntents`
- Entrypoint: `IntentsSDK.signAndSendWithdrawalIntent` with a caller-supplied `feeEstimation` (skips `_estimateWithdrawalFee`'s `FeeExceedsAmountError` and re-validates only inside `createWithdrawalIntents`)
- Attacker controls: `destinationAddress` string (`t1XVXWCvpMgBvUaed4XDqWtgQgJSu1Ghz7G`), `assetId` for a Zcash omni token, `destinationMemo`
- Exploit idea: `validateZcashAddress` uses a regex for t1/t3 with no Base58Check. Encoding path: `deriveOmniWithdrawIntentParams` -> `ft_withdraw` to `omni.bridge.near` with `msg.recipient = omniAddress(chainKind, address)`.
- Invariant to test: For every string s where `validateAddress(s, 'bip122:00040fe8ec8471911baa1db1266ea15d')` is true, the payout address derived by the Omni Bridge connector on the destination chain from the emitted intent must be the same account as s. Test: run validateAddress + createWithdrawalIntents on `t1XVXWCvpMgBvUaed4XDqWtgQgJSu1Ghz7G` and inspect the emitted memo/recipient/receiver.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: call `validateAddress('t1XVXWCvpMgBvUaed4XDqWtgQgJSu1Ghz7G', Chains.Zcash)`; then `createWithdrawalIntents` with mocked fee and assert the encoded destination byte-for-byte; compare against the omni bridge's documented accepted format.
