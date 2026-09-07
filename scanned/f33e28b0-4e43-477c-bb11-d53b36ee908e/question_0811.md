# Q0811: Dogecoin A... multisig address via PoaBridge (estimateWithdrawalFee)

## Question
Using `IntentsSDK.estimateWithdrawalFee` with `amount: 0n, feeInclusive: false` for `Dogecoin`, can `A7sEbYRT3HLGZWqkMvQ2DaiYbmgtT8vX7c` (A... multisig address) pass `validateDogeAddress` and reach `createWithdrawIntentPrimitive` -> `ft_withdraw` to the `omft.near` token with memo `WITHDRAW_TO:<address>[:<memo>]` so that the destination on chain is not the one validated, given that regex accepts A-prefix; verify PoA bridge supports P2SH payouts on Dogecoin?

## Target
- File/function: packages/intents-sdk/src/lib/validateAddress.ts `validateDogeAddress`; packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts `validateWithdrawal` / `createWithdrawalIntents`
- Entrypoint: `IntentsSDK.estimateWithdrawalFee` with `amount: 0n, feeInclusive: false` (sets `skipMinAmountValidation` and still runs `validateWithdrawal`)
- Attacker controls: `destinationAddress` string (`A7sEbYRT3HLGZWqkMvQ2DaiYbmgtT8vX7c`), `assetId` for a Dogecoin poa token, `destinationMemo`
- Exploit idea: regex accepts A-prefix; verify PoA bridge supports P2SH payouts on Dogecoin. Encoding path: `createWithdrawIntentPrimitive` -> `ft_withdraw` to the `omft.near` token with memo `WITHDRAW_TO:<address>[:<memo>]`.
- Invariant to test: For every string s where `validateAddress(s, 'bip122:1a91e3dace36e2be3bf030a65679fe82')` is true, the payout address derived by the PoA bridge relayer (bridge.chaindefuser.com) from the emitted intent must be the same account as s. Test: run validateAddress + createWithdrawalIntents on `A7sEbYRT3HLGZWqkMvQ2DaiYbmgtT8vX7c` and inspect the emitted memo/recipient/receiver.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: call `validateAddress('A7sEbYRT3HLGZWqkMvQ2DaiYbmgtT8vX7c', Chains.Dogecoin)`; then `createWithdrawalIntents` with mocked fee and assert the encoded destination byte-for-byte; compare against the poa bridge's documented accepted format.
