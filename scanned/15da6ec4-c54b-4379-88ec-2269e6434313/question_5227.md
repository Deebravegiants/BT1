# Q5227: TON raw address with workchain 1 via HotBridge (estimateWithdrawalFee)

## Question
If a counterparty supplies `destinationAddress` = `1:64c41584e067fd81ddac35b9b5489eb35d69db03acb0a01be9014421057258fd` (raw address with workchain 1) for a TON withdrawal via `IntentsSDK.estimateWithdrawalFee` with `amount: 0n, feeInclusive: false`, does `validateTonAddress` return true while `hotSdk.buildGaslessWithdrawIntent` -> `mt_withdraw` on `v2_1.omni.hot.tg` with `receiver` encodes a value the HOT Omni bridge relayer interprets differently, breaking address-validated == address-paid?

## Target
- File/function: packages/intents-sdk/src/lib/validateAddress.ts `validateTonAddress`; packages/intents-sdk/src/bridges/hot-bridge/hot-bridge.ts `validateWithdrawal` / `createWithdrawalIntents`
- Entrypoint: `IntentsSDK.estimateWithdrawalFee` with `amount: 0n, feeInclusive: false` (sets `skipMinAmountValidation` and still runs `validateWithdrawal`)
- Attacker controls: `destinationAddress` string (`1:64c41584e067fd81ddac35b9b5489eb35d69db03acb0a01be9014421057258fd`), `assetId` for a TON hot token, `destinationMemo`
- Exploit idea: rejected by workchain check; confirm the hash path `parseTonAddress` accepts it while validator rejects. Encoding path: `hotSdk.buildGaslessWithdrawIntent` -> `mt_withdraw` on `v2_1.omni.hot.tg` with `receiver`.
- Invariant to test: For every string s where `validateAddress(s, 'tvm:-239')` is true, the payout address derived by the HOT Omni bridge relayer from the emitted intent must be the same account as s. Test: run validateAddress + createWithdrawalIntents on `1:64c41584e067fd81ddac35b9b5489eb35d69db03acb0a01be9014421057258fd` and inspect the emitted memo/recipient/receiver.
- Expected Immunefi impact: Critical - funds delivered to a wrong address/chain/contract with no recovery (HackenProof: cross-chain address validation / withdrawal processing; Immunefi class: direct theft or permanent loss of user funds)
- Fast validation: vitest: call `validateAddress('1:64c41584e067fd81ddac35b9b5489eb35d69db03acb0a01be9014421057258fd', Chains.TON)`; then `createWithdrawalIntents` with mocked fee and assert the encoded destination byte-for-byte; compare against the hot bridge's documented accepted format.
