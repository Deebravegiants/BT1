# Q5122: Deadline coupling ton_connect storage_deposit via `IntentPayloadBuilde

## Question
A `storage_deposit` intent (`contract_id` = omni.bridge.near, `deposit_for_account_id`, `amount` = nativeFee) signed with `ton_connect` through `IntentPayloadBuilder.build()` gets nonce deadline == payload deadline. Since intents.near enforces both the payload `deadline` and the nonce-embedded deadline, can an unprivileged holder of the signed payload exploit the window where they differ (or a builder `setDeadline` far in the future with a nonce deadline derived from it) to execute the payload later than the caller assumed, e.g. after the caller believes `invalidateNonces` covered it?

## Target
- File/function: packages/intents-sdk/src/intents/intent-payload-builder.ts `buildWithSalt`; intent-payload-factory.ts `defaultIntentPayloadFactory` (DEFAULT_NONCE_DEADLINE_OFFSET_MS); expirable-nonce.ts `encodeNonce`; sdk.ts `invalidateNonces`
- Entrypoint: `IntentsSDK.intentBuilder()` / `signAndSendIntent`
- Attacker controls: `deadline`, nonce bytes, timing of invalidation
- Exploit idea: Two code paths derive nonce deadlines differently; invalidation picks min(now+60s, nonceDeadline) and relies on relayer memory.
- Invariant to test: a payload is never executable after min(payload.deadline, nonce.deadline), and invalidation lands before that instant.
- Expected Immunefi impact: Critical - a signed payload replayed or executed twice / on another contract (HackenProof: cross-chain replay, nonce management; Immunefi class: direct theft of user funds)
- Fast validation: vitest with fake timers: build via both paths, decode nonce, compare deadlines; simulate invalidate ordering.
