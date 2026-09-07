# Q0843: Dogecoin D address length 34 vs 35 boundary via PoaBridge (estimateWithdrawalFee)

## Question
If a counterparty supplies `destinationAddress` = `DH5yaieqoZN36fDVciNyRueRGvGLR3mr7LX` (D address length 34 vs 35 boundary) for a Dogecoin withdrawal via `IntentsSDK.estimateWithdrawalFee` with `amount: 0n, feeInclusive: false`, does `validateDogeAddress` return true while `createWithdrawIntentPrimitive` -> `ft_withdraw` to the `omft.near` token with memo `WITHDRAW_TO:<address>[:<memo>]` encodes a value the PoA bridge relayer (bridge.chaindefuser.com) interprets differently, breaking address-validated == address-paid?

## Target
- File/function: packages/intents-sdk/src/lib/validateAddress.ts `validateDogeAddress`; packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts `validateWithdrawal` / `createWithdrawalIntents`
- Entrypoint: `IntentsSDK.estimateWithdrawalFee` with `amount: 0n, feeInclusive: false` (sets `skipMinAmountValidation` and still runs `validateWithdrawal`)
- Attacker controls: `destinationAddress` string (`DH5yaieqoZN36fDVciNyRueRGvGLR3mr7LX`), `assetId` for a Dogecoin poa token, `destinationMemo`
- Exploit idea: `{25,33}` bounds vs real Doge lengths; confirm valid long addresses are not rejected while short garbage passes. Encoding path: `createWithdrawIntentPrimitive` -> `ft_withdraw` to the `omft.near` token with memo `WITHDRAW_TO:<address>[:<memo>]`.
- Invariant to test: For every string s where `validateAddress(s, 'bip122:1a91e3dace36e2be3bf030a65679fe82')` is true, the payout address derived by the PoA bridge relayer (bridge.chaindefuser.com) from the emitted intent must be the same account as s. Test: run validateAddress + createWithdrawalIntents on `DH5yaieqoZN36fDVciNyRueRGvGLR3mr7LX` and inspect the emitted memo/recipient/receiver.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: call `validateAddress('DH5yaieqoZN36fDVciNyRueRGvGLR3mr7LX', Chains.Dogecoin)`; then `createWithdrawalIntents` with mocked fee and assert the encoded destination byte-for-byte; compare against the poa bridge's documented accepted format.
