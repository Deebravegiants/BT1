# Q2745: Batch fee cache nep141:bera.omft.near: two entries for the same token with 

## Question
Calling `IntentsSDK.estimateWithdrawalFee` with an array containing `nep141:bera.omft.near` where two entries for the same token with different destinations share one `getCachedSupportedTokens` / `storageDepositCache` / `destinationChainAddressCache` entry, `Promise.all` runs `_estimateWithdrawalFee` concurrently per element. Can an unprivileged user shape the batch so that one element's fee, minimum or storage-deposit result is computed from another element's cached state (or a stale cache filled by the concurrent sibling), producing a `FeeEstimation[]` that, when fed to `signAndSendWithdrawalIntent`, debits more than displayed or signs an amount below the destination minimum?

## Target
- File/function: packages/intents-sdk/src/sdk.ts `estimateWithdrawalFee` (Promise.all), `_estimateWithdrawalFee`; poa-bridge.ts `getCachedSupportedTokens`; omni-bridge.ts `getCachedStorageDepositValue`, `getCachedDestinationTokenAddress`, `getCachedIntentsStorageBalance`; direct-bridge.ts `getCachedStorageDepositValue`
- Entrypoint: `IntentsSDK.estimateWithdrawalFee(WithdrawalParams[])` then `signAndSendWithdrawalIntent`
- Attacker controls: batch composition and ordering, `feeInclusive` per element
- Exploit idea: Caches are keyed coarsely (token, or token+account) and populated only on 'sufficient' results; concurrent estimates for related elements race on the same keys.
- Invariant to test: FeeEstimation[i] is exactly what a standalone estimate for withdrawalParams[i] would return at that instant.
- Expected Immunefi impact: High - fee overcharge or solver overpaid beyond the displayed fee (HackenProof: fee estimation calculations)
- Fast validation: vitest: mock RPC/HTTP with call counters; run batch vs individual estimates and diff results.
