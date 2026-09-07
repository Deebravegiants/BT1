# Q3580: Omni status Abstract: the destination chain kind is not in the

## Question
On Omni bridge to Abstract, when the destination chain kind is not in the EVM/Sol/Fogo/Strk/Aptos/UTXO list so `completed, txHash: null` is returned immediately, does `OmniBridge.describeWithdrawal` (`getTransfer()[args.index]`) return `completed` or a `txHash` for a transfer that is not the user's, so `processWithdrawal` resolves with a destinationTx that an integrator books as delivered?

## Target
- File/function: packages/intents-sdk/src/bridges/omni-bridge/omni-bridge.ts `describeWithdrawal`, `createWithdrawalIdentifier`
- Entrypoint: `IntentsSDK.waitForWithdrawalCompletion`
- Attacker controls: batch shape and destination chain
- Exploit idea: Index-based lookup into an externally ordered list; early `completed` for unknown chain kinds.
- Invariant to test: reported txHash finalises the transfer whose recipient == user's destination and amount == signed amount.
- Expected Immunefi impact: High - status/hash misreport making an integrator credit or refund twice (HackenProof: withdrawal processing / serialization correctness)
- Fast validation: vitest: mock `getTransfer` and assert per-index results.
