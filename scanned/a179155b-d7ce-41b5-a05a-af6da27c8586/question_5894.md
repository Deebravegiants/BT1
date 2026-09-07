# Q5894: Sig transform sep53: `userAddress` is a muxed M-address via `publishIntent` (inter

## Question
For `sep53` through `publishIntent` (internal-utils) via `prepareSwapSignedData`, when `userAddress` is a muxed M-address, does the signature/public-key transform (`stellarAddressToBytes` slices payload assuming G-address layout) produce a `MultiPayload` whose `signature` or `public_key` does not correspond to the payload the user approved, so the relayer rejects it after the user's wallet approved a withdrawal (funds stay but the integrator's flow records a signed intent), or worse a different key is presented as the signer?

## Target
- File/function: packages/intents-sdk/src/intents/intent-signer-impl/intent-signer-nep413.ts `signRaw`; intent-signer-viem.ts; packages/internal-utils/src/utils/prepareBroadcastRequest.ts `transformERC191Signature`, `normalizeERC191Signature`, `transformNEP141Signature`; multiPayload/webauthn.ts; webAuthn.ts `extractRawSignature`
- Entrypoint: `publishIntent` (internal-utils) via `prepareSwapSignedData`
- Attacker controls: the wallet's signature/public-key bytes and the `userAddress` string
- Exploit idea: `stellarAddressToBytes` slices payload assuming G-address layout
- Invariant to test: MultiPayload.signature verifies over MultiPayload.payload under MultiPayload.public_key, and that key is the caller's.
- Expected Immunefi impact: High - signature bound to the wrong contract, signer or nonce (HackenProof: intent signing and verification, nonce management)
- Fast validation: vitest: feed the described signature format through the transform and verify with the corresponding curve library.
