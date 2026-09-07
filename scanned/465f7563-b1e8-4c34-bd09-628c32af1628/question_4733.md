# Q4733: Settlement parse: `TX_BROADCASTED` then `NOT_FOUND_OR_NO via processWithdrawal`

## Question
Through `IntentsSDK.processWithdrawal`, when `TX_BROADCASTED` then `NOT_FOUND_OR_NOT_VALID` + `FAILED`, does the relay-client parsing in `parsePublishIntentsResponse` / `waitForIntentSettlement` (IntentSettlementError after onTxHashKnown fired) make the SDK return a success or tx hash that does not correspond to an executed intent, so an integrator releases funds or credits a user for an intent that never settled?

## Target
- File/function: packages/internal-utils/src/solverRelay/publishIntents.ts `parsePublishIntentsResponse`; waitForIntentSettlement.ts; packages/intents-sdk/src/intents/intent-relayer-impl/intent-relayer-public.ts
- Entrypoint: `IntentsSDK.processWithdrawal`
- Attacker controls: the intent the user submits (and therefore which relay response branch is hit); relay responses are data the SDK must interpret correctly
- Exploit idea: IntentSettlementError after onTxHashKnown fired
- Invariant to test: a returned intentHash/txHash always identifies an intent that was accepted and, for waitForIntentSettlement, executed on chain.
- Expected Immunefi impact: High - status/hash misreport making an integrator credit or refund twice (HackenProof: withdrawal processing / serialization correctness)
- Fast validation: vitest: mock JSON-RPC responses for each branch and assert thrown vs returned values.
