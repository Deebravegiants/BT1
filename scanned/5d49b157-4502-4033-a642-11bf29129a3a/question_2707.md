# Q2707: Sig transform erc191: EIP-1271 smart-account signature (not 65 via `IntentsSDK.signAndSen #2707

## Question
For `erc191` through `IntentsSDK.signAndSendWithdrawalIntent`, when EIP-1271 smart-account signature (not 65 bytes), does the signature/public-key transform (`normalizeERC191Signature` slices the last 2 chars regardless) produce a `MultiPayload` whose `signature` or `public_key` does not correspond to the payload the user approved, so the relayer rejects it after the user's wallet approved a withdrawal (funds stay but the integrator's flow records a signed intent), or worse a different key is presented as the signer?

## Target
- File/function: packages/intents-sdk/src/intents/intent-signer-impl/intent-signer-nep413.ts `signRaw`; intent-signer-viem.ts; packages/internal-utils/src/utils/prepareBroadcastRequest.ts `transformERC191Signature`, `normalizeERC191Signature`, `transformNEP141Signature`; multiPayload/webauthn.ts; webAuthn.ts `extractRawSignature`
- Entrypoint: `IntentsSDK.signAndSendWithdrawalIntent`
- Attacker controls: the wallet's signature/public-key bytes and the `userAddress` string
- Exploit idea: `normalizeERC191Signature` slices the last 2 chars regardless
- Invariant to test: MultiPayload.signature verifies over MultiPayload.payload under MultiPayload.public_key, and that key is the caller's.
- Expected Immunefi impact: High - signature bound to the wrong contract, signer or nonce (HackenProof: intent signing and verification, nonce management)
- Fast validation: vitest: feed the described signature format through the transform and verify with the corresponding curve library.
