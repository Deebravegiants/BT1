# Q5563: Identity near: an uppercase NEAR account id / `prepareSwapSigned

## Question
For auth method `near` with an uppercase NEAR account id, does `authHandleToIntentsUserId` produce an `IntentsUserId` that either collides with another credential or differs from the id intents.near derives from the signature's public key, so that in `prepareSwapSignedData` public_key derivation the payload's `signer_id` names an account the attached key does not control (or two users share one balance key)?

## Target
- File/function: packages/internal-utils/src/utils/authIdentity.ts `authHandleToIntentsUserId`, `webAuthnIdentifierToIntentsUserId`; tronAddressToHex.ts; stellarAddressToBytes.ts; prepareBroadcastRequest.ts
- Entrypoint: `IntentsSDK.signAndSendIntent` (Viem signer) / `publishIntent` (internal-utils)
- Attacker controls: the `near` identifier string
- Exploit idea: lowercased for user id but `validateNearAddress` rejects uppercase in `setSigner`
- Invariant to test: signer_id == intents.near's canonical id for the public key that produced the signature; the mapping is injective over valid credentials.
- Expected Immunefi impact: High - signature bound to the wrong contract, signer or nonce (HackenProof: intent signing and verification, nonce management)
- Fast validation: vitest: feed the crafted identifier through the mapping and compare with the contract's derivation rules for that standard.
