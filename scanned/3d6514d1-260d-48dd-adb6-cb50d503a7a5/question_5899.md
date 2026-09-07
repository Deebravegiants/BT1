# Q5899: AuroraEngineBridge storage deposit: `userStorageBalance` is read for the wro

## Question
In AuroraEngineBridge, when `userStorageBalance` is read for the wrong account (destination vs bridge contract), does the `storageDepositFee` folded into `feeEstimation.amount` (via `getFeeQuote` token_diff) and the `storage_deposit` field of `ft_withdraw` diverge, so the user pays a storage deposit twice, or the withdrawal reverts on the token contract and the tokens sit at intents.near / the bridge until manually refunded?

## Target
- File/function: packages/intents-sdk/src/bridges/aurora-engine-bridge/aurora-engine-bridge.ts `estimateWithdrawalFee`, `Promise.all(min, balance for auroraEngineContractId)`, `createWithdrawalIntents`
- Entrypoint: `IntentsSDK.processWithdrawal` (estimate then sign later) / `signAndSendWithdrawalIntent` with stale `feeEstimation`
- Attacker controls: timing between estimate and sign, destination account, `feeEstimation` reuse
- Exploit idea: Storage values are cached for up to 1h only when already sufficient; the fee quote and the `storage_deposit` intent field are derived from the same stale number without re-validation at sign time.
- Invariant to test: storage_deposit attached == max(0, minStorageBalance - balance(destination)) at execution time, charged once.
- Expected Immunefi impact: High - withdrawal stuck or refunded to the wrong account until manual intervention (HackenProof: withdrawal processing; Immunefi class: temporary freezing of funds)
- Fast validation: vitest: mock NEAR RPC `storage_balance_of` changing between calls; inspect intents and fee.
