# Q2016: Sig transform erc191: signature with v = 27/28 vs 0/1 vs 0x1b/ via `publishIntent` (inter

## Question
For `erc191` through `publishIntent` (internal-utils) via `prepareSwapSignedData`, when signature with v = 27/28 vs 0/1 vs 0x1b/0x1c, does the signature/public-key transform (`toRecoveryBit` maps 27/28; other values throw after the user signed) produce a `MultiPayload` whose `signature` or `public_key` does not correspond to the payload the user approved, so the relayer rejects it after the user's wallet approved a withdrawal (funds stay but the integrator's flow records a signed intent), or worse a different key is presented as the signer?

## Target
- File/function: packages/intents-sdk/src/intents/intent-signer-impl/intent-signer-nep413.ts `signRaw`; intent-signer-viem.ts; packages/internal-utils/src/utils/prepareBroadcastRequest.ts `transformERC191Signature`, `normalizeERC191Signature`, `transformNEP141Signature`; multiPayload/webauthn.ts; webAuthn.ts `extractRawSignature`
- Entrypoint: `publishIntent` (internal-utils) via `prepareSwapSignedData`
- Attacker controls: the wallet's signature/public-key bytes and the `userAddress` string
- Exploit idea: `toRecoveryBit` maps 27/28; other values throw after the user signed
- Invariant to test: MultiPayload.signature verifies over MultiPayload.payload under MultiPayload.public_key, and that key is the caller's.
- Expected Immunefi impact: High - signature bound to the wrong contract, signer or nonce (HackenProof: intent signing and verification, nonce management)
- Fast validation: vitest: feed the described signature format through the transform and verify with the corresponding curve library.
