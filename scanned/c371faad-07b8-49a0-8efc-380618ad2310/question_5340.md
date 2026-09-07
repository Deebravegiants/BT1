# Q5340: Settlement parse: relay returns fewer `intent_hashes` th via sendSignedIntents`

## Question
Through `IntentsSDK.sendSignedIntents`, when relay returns fewer `intent_hashes` than payloads published, does the relay-client parsing in `parsePublishIntentsResponse` / `waitForIntentSettlement` (`tickets[beforeCount]` may be undefined and cast to Ticket) make the SDK return a success or tx hash that does not correspond to an executed intent, so an integrator releases funds or credits a user for an intent that never settled?

## Target
- File/function: packages/internal-utils/src/solverRelay/publishIntents.ts `parsePublishIntentsResponse`; waitForIntentSettlement.ts; packages/intents-sdk/src/intents/intent-relayer-impl/intent-relayer-public.ts
- Entrypoint: `IntentsSDK.sendSignedIntents`
- Attacker controls: the intent the user submits (and therefore which relay response branch is hit); relay responses are data the SDK must interpret correctly
- Exploit idea: `tickets[beforeCount]` may be undefined and cast to Ticket
- Invariant to test: a returned intentHash/txHash always identifies an intent that was accepted and, for waitForIntentSettlement, executed on chain.
- Expected Immunefi impact: High - status/hash misreport making an integrator credit or refund twice (HackenProof: withdrawal processing / serialization correctness)
- Fast validation: vitest: mock JSON-RPC responses for each branch and assert thrown vs returned values.
