# Q0824: Dogecoin D address length 34 vs 35 boundary via PoaBridge (signAndSendWithdrawalIntent)

## Question
Using `IntentsSDK.signAndSendWithdrawalIntent` with a caller-supplied `feeEstimation` for `Dogecoin`, can `DH5yaieqoZN36fDVciNyRueRGvGLR3mr7LX` (D address length 34 vs 35 boundary) pass `validateDogeAddress` and reach `createWithdrawIntentPrimitive` -> `ft_withdraw` to the `omft.near` token with memo `WITHDRAW_TO:<address>[:<memo>]` so that the destination on chain is not the one validated, given that `{25,33}` bounds vs real Doge lengths; confirm valid long addresses are not rejected while short garbage passes?

## Target
- File/function: packages/intents-sdk/src/lib/validateAddress.ts `validateDogeAddress`; packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts `validateWithdrawal` / `createWithdrawalIntents`
- Entrypoint: `IntentsSDK.signAndSendWithdrawalIntent` with a caller-supplied `feeEstimation` (skips `_estimateWithdrawalFee`'s `FeeExceedsAmountError` and re-validates only inside `createWithdrawalIntents`)
- Attacker controls: `destinationAddress` string (`DH5yaieqoZN36fDVciNyRueRGvGLR3mr7LX`), `assetId` for a Dogecoin poa token, `destinationMemo`
- Exploit idea: `{25,33}` bounds vs real Doge lengths; confirm valid long addresses are not rejected while short garbage passes. Encoding path: `createWithdrawIntentPrimitive` -> `ft_withdraw` to the `omft.near` token with memo `WITHDRAW_TO:<address>[:<memo>]`.
- Invariant to test: For every string s where `validateAddress(s, 'bip122:1a91e3dace36e2be3bf030a65679fe82')` is true, the payout address derived by the PoA bridge relayer (bridge.chaindefuser.com) from the emitted intent must be the same account as s. Test: run validateAddress + createWithdrawalIntents on `DH5yaieqoZN36fDVciNyRueRGvGLR3mr7LX` and inspect the emitted memo/recipient/receiver.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: call `validateAddress('DH5yaieqoZN36fDVciNyRueRGvGLR3mr7LX', Chains.Dogecoin)`; then `createWithdrawalIntents` with mocked fee and assert the encoded destination byte-for-byte; compare against the poa bridge's documented accepted format.
