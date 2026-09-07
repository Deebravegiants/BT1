# Q2286: Identity ton: a 64-hex identifier that is not the hash / `makeInnerSwapMess

## Question
For auth method `ton` with a 64-hex identifier that is not the hash of the signing wallet, does `authHandleToIntentsUserId` produce an `IntentsUserId` that either collides with another credential or differs from the id intents.near derives from the signature's public key, so that in `makeInnerSwapMessage` / `makeInnerTransferMessage` signer_id the payload's `signer_id` names an account the attached key does not control (or two users share one balance key)?

## Target
- File/function: packages/internal-utils/src/utils/authIdentity.ts `authHandleToIntentsUserId`, `webAuthnIdentifierToIntentsUserId`; tronAddressToHex.ts; stellarAddressToBytes.ts; prepareBroadcastRequest.ts
- Entrypoint: `IntentsSDK.signAndSendIntent` (Viem signer) / `publishIntent` (internal-utils)
- Attacker controls: the `ton` identifier string
- Exploit idea: only length and hex are asserted
- Invariant to test: signer_id == intents.near's canonical id for the public key that produced the signature; the mapping is injective over valid credentials.
- Expected Immunefi impact: High - signature bound to the wrong contract, signer or nonce (HackenProof: intent signing and verification, nonce management)
- Fast validation: vitest: feed the crafted identifier through the mapping and compare with the contract's derivation rules for that standard.
