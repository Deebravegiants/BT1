# Q2060: invalidateNonces tip191: a legacy 32-byte random nonc / `publishIntents` returns `

## Question
Calling `invalidateNonces` with a legacy 32-byte random nonce using a `tip191` signer, when `publishIntents` returns `already processed`, does the SDK report success while the original signed payload remains executable (on-chain or via another relayer/route), letting anyone holding that payload execute the user's withdrawal after the user believes it cancelled?

## Target
- File/function: packages/intents-sdk/src/sdk.ts `invalidateNonces`; intent-payload-builder.ts `setNonce`; expirable-nonce.ts `decodeNonce`, `saltedNonceSchema`
- Entrypoint: `IntentsSDK.invalidateNonces`
- Attacker controls: the nonce strings, the signer, timing
- Exploit idea: Invalidation is best-effort and relayer-memory only (comment dated 15 Nov 2025); deadline logic depends on decodeNonce succeeding; signer_id mismatch makes the on-chain nonce namespace different.
- Invariant to test: after invalidateNonces resolves, no payload with those nonces can execute for that signer.
- Expected Immunefi impact: Critical - a signed payload replayed or executed twice / on another contract (HackenProof: cross-chain replay, nonce management; Immunefi class: direct theft of user funds)
- Fast validation: vitest: mock publish responses; assert the empty intents' signer_id/deadline; reason about on-chain namespace.
