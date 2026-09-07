# Q2722: Adi all-lowercase address via HotBridge (estimateWithdrawalFee)

## Question
Using `IntentsSDK.estimateWithdrawalFee` with `amount: 0n, feeInclusive: false` for `Adi`, can `0xdac17f958d2ee523a2206206994597c13d831ec7` (all-lowercase address) pass `validateEthAddress` and reach `hotSdk.buildGaslessWithdrawIntent` -> `mt_withdraw` on `v2_1.omni.hot.tg` with `receiver` so that the destination on chain is not the one validated, given that strict mode accepts all-lowercase; `compareAddresses` uses `getAddress` so token-address block works, but the memo/recipient is lowercase?

## Target
- File/function: packages/intents-sdk/src/lib/validateAddress.ts `validateEthAddress`; packages/intents-sdk/src/bridges/hot-bridge/hot-bridge.ts `validateWithdrawal` / `createWithdrawalIntents`
- Entrypoint: `IntentsSDK.estimateWithdrawalFee` with `amount: 0n, feeInclusive: false` (sets `skipMinAmountValidation` and still runs `validateWithdrawal`)
- Attacker controls: `destinationAddress` string (`0xdac17f958d2ee523a2206206994597c13d831ec7`), `assetId` for a Adi hot token, `destinationMemo`
- Exploit idea: strict mode accepts all-lowercase; `compareAddresses` uses `getAddress` so token-address block works, but the memo/recipient is lowercase. Encoding path: `hotSdk.buildGaslessWithdrawIntent` -> `mt_withdraw` on `v2_1.omni.hot.tg` with `receiver`.
- Invariant to test: For every string s where `validateAddress(s, 'eip155:36900')` is true, the payout address derived by the HOT Omni bridge relayer from the emitted intent must be the same account as s. Test: run validateAddress + createWithdrawalIntents on `0xdac17f958d2ee523a2206206994597c13d831ec7` and inspect the emitted memo/recipient/receiver.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: call `validateAddress('0xdac17f958d2ee523a2206206994597c13d831ec7', Chains.Adi)`; then `createWithdrawalIntents` with mocked fee and assert the encoded destination byte-for-byte; compare against the hot bridge's documented accepted format.
