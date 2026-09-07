# Q5812: Cardano Byron base58 address via PoaBridge (estimateWithdrawalFee)

## Question
Using `IntentsSDK.estimateWithdrawalFee` with `amount: 0n, feeInclusive: false` for `Cardano`, can `DdzFFzCqrhsjZHKn5Y4dBHsyPQXeF6tE7nKz6RA4ctpAWr6bvQYbcnAiiqoV5iQEg12yTAcavR3DoHxfUgzVoDoiAfdAtaxB6bFDLZUR` (Byron base58 address) pass `validateCardanoAddress` and reach `createWithdrawIntentPrimitive` -> `ft_withdraw` to the `omft.near` token with memo `WITHDRAW_TO:<address>[:<memo>]` so that the destination on chain is not the one validated, given that bech32 decode fails -> false; but does the PoA bridge accept Byron??

## Target
- File/function: packages/intents-sdk/src/lib/validateAddress.ts `validateCardanoAddress`; packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts `validateWithdrawal` / `createWithdrawalIntents`
- Entrypoint: `IntentsSDK.estimateWithdrawalFee` with `amount: 0n, feeInclusive: false` (sets `skipMinAmountValidation` and still runs `validateWithdrawal`)
- Attacker controls: `destinationAddress` string (`DdzFFzCqrhsjZHKn5Y4dBHsyPQXeF6tE7nKz6RA4ctpAWr6bvQYbcnAiiqoV5iQEg12yTAcavR3DoHxfUgzVoDoiAfdAtaxB6bFDLZUR`), `assetId` for a Cardano poa token, `destinationMemo`
- Exploit idea: bech32 decode fails -> false; but does the PoA bridge accept Byron?. Encoding path: `createWithdrawIntentPrimitive` -> `ft_withdraw` to the `omft.near` token with memo `WITHDRAW_TO:<address>[:<memo>]`.
- Invariant to test: For every string s where `validateAddress(s, 'cip34:1-764824073')` is true, the payout address derived by the PoA bridge relayer (bridge.chaindefuser.com) from the emitted intent must be the same account as s. Test: run validateAddress + createWithdrawalIntents on `DdzFFzCqrhsjZHKn5Y4dBHsyPQXeF6tE7nKz6RA4ctpAWr6bvQYbcnAiiqoV5iQEg12yTAcavR3DoHxfUgzVoDoiAfdAtaxB6bFDLZUR` and inspect the emitted memo/recipient/receiver.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: call `validateAddress('DdzFFzCqrhsjZHKn5Y4dBHsyPQXeF6tE7nKz6RA4ctpAWr6bvQYbcnAiiqoV5iQEg12yTAcavR3DoHxfUgzVoDoiAfdAtaxB6bFDLZUR', Chains.Cardano)`; then `createWithdrawalIntents` with mocked fee and assert the encoded destination byte-for-byte; compare against the poa bridge's documented accepted format.
