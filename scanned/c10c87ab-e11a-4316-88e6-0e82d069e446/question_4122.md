# Q4122: quoteHashes OmniBridge: an expired quote hash is included so the rel

## Question
For a OmniBridge withdrawal through `signAndSendWithdrawalIntent`, when an expired quote hash is included so the relayer rejects the whole atomic batch after signing, does `relayParamsFn` build a `quote_hashes` list inconsistent with the signed `token_diff` intents, so the relayer settles the user's `token_diff` against a solver quote the user never priced (overpaying the solver) or fails the batch after the user signed?

## Target
- File/function: packages/intents-sdk/src/sdk.ts `signAndSendWithdrawalIntent` (relayParamsFn), `signAndSendIntent`; intent-executer.ts (quoteHashes in publishIntents)
- Entrypoint: `IntentsSDK.signAndSendWithdrawalIntent` / `signAndSendIntent` with `relayParams`
- Attacker controls: `intent.relayParams`, `feeEstimation[].quote`
- Exploit idea: quote hashes are aggregated by concatenation with no cross-check against `token_diff` contents or expiry.
- Invariant to test: quote_hashes == exactly the quotes backing the token_diff intents in the published payloads.
- Expected Immunefi impact: High - fee overcharge or solver overpaid beyond the displayed fee (HackenProof: fee estimation calculations)
- Fast validation: vitest: capture `publish_intents` params and diff quote_hashes vs intents.
