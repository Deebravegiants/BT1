# Q0152: Settlement parse: `publish_intents` returns `status: FAI via signAndSendIntent`

## Question
Through `IntentsSDK.signAndSendIntent`, when `publish_intents` returns `status: FAILED, reason: 'already processed'`, does the relay-client parsing in `parsePublishIntentsResponse` / `waitForIntentSettlement` (treated as OK and `intent_hashes` returned; the caller believes a fresh publish succeeded) make the SDK return a success or tx hash that does not correspond to an executed intent, so an integrator releases funds or credits a user for an intent that never settled?

## Target
- File/function: packages/internal-utils/src/solverRelay/publishIntents.ts `parsePublishIntentsResponse`; waitForIntentSettlement.ts; packages/intents-sdk/src/intents/intent-relayer-impl/intent-relayer-public.ts
- Entrypoint: `IntentsSDK.signAndSendIntent`
- Attacker controls: the intent the user submits (and therefore which relay response branch is hit); relay responses are data the SDK must interpret correctly
- Exploit idea: treated as OK and `intent_hashes` returned; the caller believes a fresh publish succeeded
- Invariant to test: a returned intentHash/txHash always identifies an intent that was accepted and, for waitForIntentSettlement, executed on chain.
- Expected Immunefi impact: High - status/hash misreport making an integrator credit or refund twice (HackenProof: withdrawal processing / serialization correctness)
- Fast validation: vitest: mock JSON-RPC responses for each branch and assert thrown vs returned values.
