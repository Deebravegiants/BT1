# Q5201: Sig transform ton_connect: `signature` base64 with padding vs base6 via `IntentsSDK.sendSigned

## Question
For `ton_connect` through `IntentsSDK.sendSignedIntents`, when `signature` base64 with padding vs base64url, does the signature/public-key transform (`base64.decode` then base58; padding mismatch throws after signing) produce a `MultiPayload` whose `signature` or `public_key` does not correspond to the payload the user approved, so the relayer rejects it after the user's wallet approved a withdrawal (funds stay but the integrator's flow records a signed intent), or worse a different key is presented as the signer?

## Target
- File/function: packages/intents-sdk/src/intents/intent-signer-impl/intent-signer-nep413.ts `signRaw`; intent-signer-viem.ts; packages/internal-utils/src/utils/prepareBroadcastRequest.ts `transformERC191Signature`, `normalizeERC191Signature`, `transformNEP141Signature`; multiPayload/webauthn.ts; webAuthn.ts `extractRawSignature`
- Entrypoint: `IntentsSDK.sendSignedIntents`
- Attacker controls: the wallet's signature/public-key bytes and the `userAddress` string
- Exploit idea: `base64.decode` then base58; padding mismatch throws after signing
- Invariant to test: MultiPayload.signature verifies over MultiPayload.payload under MultiPayload.public_key, and that key is the caller's.
- Expected Immunefi impact: High - signature bound to the wrong contract, signer or nonce (HackenProof: intent signing and verification, nonce management)
- Fast validation: vitest: feed the described signature format through the transform and verify with the corresponding curve library.
