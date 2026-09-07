# Q2842: HOT status Adi: `parseWithdrawalNonces` returns nonces i

## Question
On HOT bridge to Adi, when `parseWithdrawalNonces` returns nonces in a different order than the `mt_withdraw` intents, does `HotBridge.describeWithdrawal` report a `completed` status or `txHash` that does not correspond to the user's withdrawal at `index`, so an exchange integrator credits the user for a transfer that went to someone else or never landed?

## Target
- File/function: packages/intents-sdk/src/bridges/hot-bridge/hot-bridge.ts `describeWithdrawal`, `fetchWithdrawalHashBridgeIndexer`, `fetchWithdrawalHashFromApi`; hot-bridge-utils.ts `formatTxHash`
- Entrypoint: `IntentsSDK.waitForWithdrawalCompletion`
- Attacker controls: batch order and per-chain sequencing; the HOT-side responses are data the SDK must validate
- Exploit idea: Nonce->index mapping is positional per NEAR tx; indexer/API results are matched by nonce string equality; non-hex statuses degrade to `completed, txHash: null`.
- Invariant to test: txHash returned for index i is the destination tx that paid withdrawal i's receiver and amount.
- Expected Immunefi impact: High - status/hash misreport making an integrator credit or refund twice (HackenProof: withdrawal processing / serialization correctness)
- Fast validation: vitest: mock `parseWithdrawalNonces`, indexer and API with conflicting data; assert output per index.
