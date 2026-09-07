# Q1039: Sig transform nep413: `publicKey` in `secp256k1:` format from  via `IntentsSDK.signAndSen #1039

## Question
For `nep413` through `IntentsSDK.signAndSendWithdrawalIntent`, when `publicKey` in `secp256k1:` format from a wallet, does the signature/public-key transform (`public_key` forwarded verbatim; contract expects ed25519 for NEP-413) produce a `MultiPayload` whose `signature` or `public_key` does not correspond to the payload the user approved, so the relayer rejects it after the user's wallet approved a withdrawal (funds stay but the integrator's flow records a signed intent), or worse a different key is presented as the signer?

## Target
- File/function: packages/intents-sdk/src/intents/intent-signer-impl/intent-signer-nep413.ts `signRaw`; intent-signer-viem.ts; packages/internal-utils/src/utils/prepareBroadcastRequest.ts `transformERC191Signature`, `normalizeERC191Signature`, `transformNEP141Signature`; multiPayload/webauthn.ts; webAuthn.ts `extractRawSignature`
- Entrypoint: `IntentsSDK.signAndSendWithdrawalIntent`
- Attacker controls: the wallet's signature/public-key bytes and the `userAddress` string
- Exploit idea: `public_key` forwarded verbatim; contract expects ed25519 for NEP-413
- Invariant to test: MultiPayload.signature verifies over MultiPayload.payload under MultiPayload.public_key, and that key is the caller's.
- Expected Immunefi impact: High - signature bound to the wrong contract, signer or nonce (HackenProof: intent signing and verification, nonce management)
- Fast validation: vitest: feed the described signature format through the transform and verify with the corresponding curve library.
