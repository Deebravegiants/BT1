# Q5253: Serialize nep141:plasma.omft.near under erc191

## Question
A withdrawal of `nep141:plasma.omft.near` (PoA native XPL) is signed with `erc191` (`IntentSignerViem.signIntent`; `payload` = JSON of {signer_id, verifying_contract, deadline, nonce, intents}). The intent carries bigint amounts as strings and free-text `memo`/`msg`. `IntentSignerViem`/`IntentSignerNEP413` use compact `JSON.stringify`, while internal-utils `makeSwapMessage` pretty-prints with `JSON.stringify(payload, null, 2)` for ERC-191/TON/Tron/Stellar. Can an unprivileged user craft a `destinationAddress`/`destinationMemo` containing quotes, unicode escapes or line breaks so that the JSON the wallet displays and signs differs from the JSON intents.near parses (or from what `computeIntentHash` hashes), letting the executed `receiver_id`/`memo`/`amount` differ from what the user approved?

## Target
- File/function: packages/intents-sdk/src/intents/intent-signer-impl/intent-signer-nep413.ts `signIntent`; intent-signer-viem.ts `signIntent`; packages/internal-utils/src/utils/messageFactory.ts `makeSwapMessage`; intent-hash.ts
- Entrypoint: `IntentsSDK.signAndSendWithdrawalIntent` / `intentBuilder().buildAndSign`
- Attacker controls: `destinationAddress`, `destinationMemo`, `routeConfig.msg` strings embedded into the intent JSON
- Exploit idea: Two serialisers exist for the same payload; wallets may re-serialise; the contract parses the signed string. Any divergence between displayed, hashed and executed JSON is a signing-integrity gap.
- Invariant to test: JSON.parse(signed.message/payload) deep-equals the IntentPayload the SDK built, byte-for-byte for every string field.
- Expected Immunefi impact: Critical - intent manipulation moving funds the user did not authorise (HackenProof: intent signing and verification; Immunefi class: direct theft of user funds)
- Fast validation: vitest: sign an intent whose memo contains `"`, `\n`, `\u2028` and compare parsed payload with the built payload and the computed hash.
