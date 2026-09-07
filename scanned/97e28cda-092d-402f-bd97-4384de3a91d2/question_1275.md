# Q1275: Deadline coupling erc191 native_withdraw via `IntentExecuter.sign

## Question
A `native_withdraw` intent (`receiver_id`, `amount` (Direct route for `wrap.near` without `msg`)) signed with `erc191` through `IntentExecuter.signAndSendIntent` via `defaultIntentPayloadFactory` gets nonce deadline == payload deadline + 60s. Since intents.near enforces both the payload `deadline` and the nonce-embedded deadline, can an unprivileged holder of the signed payload exploit the window where they differ (or a builder `setDeadline` far in the future with a nonce deadline derived from it) to execute the payload later than the caller assumed, e.g. after the caller believes `invalidateNonces` covered it?

## Target
- File/function: packages/intents-sdk/src/intents/intent-payload-builder.ts `buildWithSalt`; intent-payload-factory.ts `defaultIntentPayloadFactory` (DEFAULT_NONCE_DEADLINE_OFFSET_MS); expirable-nonce.ts `encodeNonce`; sdk.ts `invalidateNonces`
- Entrypoint: `IntentsSDK.intentBuilder()` / `signAndSendIntent`
- Attacker controls: `deadline`, nonce bytes, timing of invalidation
- Exploit idea: Two code paths derive nonce deadlines differently; invalidation picks min(now+60s, nonceDeadline) and relies on relayer memory.
- Invariant to test: a payload is never executable after min(payload.deadline, nonce.deadline), and invalidation lands before that instant.
- Expected Immunefi impact: Critical - a signed payload replayed or executed twice / on another contract (HackenProof: cross-chain replay, nonce management; Immunefi class: direct theft of user funds)
- Fast validation: vitest with fake timers: build via both paths, decode nonce, compare deadlines; simulate invalidate ordering.
