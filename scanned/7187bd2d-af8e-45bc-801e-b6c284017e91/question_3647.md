# Q3647: Serialization: `VersionedNonceBuilder.decodeNonce` on a 32- via `IntentsSDK.parseAsset

## Question
Reachable from `IntentsSDK.parseAssetId` / `createWithdrawalIntents`: with `VersionedNonceBuilder.decodeNonce` on a 32-byte legacy nonce whose first 4 bytes happen to equal the magic prefix (prefix check only), can an unprivileged user-controlled string cause a random legacy nonce misinterpreted as versioned in `invalidateNonces`, and does that lead to an intent being signed or published for an asset, contract or nonce other than the one the caller named?

## Target
- File/function: packages/internal-utils/src/utils/tokenUtils.ts `parseDefuseAssetId`; packages/intents-sdk/src/lib/caip2.ts; packages/crosschain-assetid/src/parse.ts, stringify.ts; expirable-nonce.ts; prepareBroadcastRequest.ts; serialize.ts
- Entrypoint: `IntentsSDK.parseAssetId` / `createWithdrawalIntents`
- Attacker controls: the asset id / chain string / nonce / signature string
- Exploit idea: prefix check only
- Invariant to test: parse(stringify(x)) == x and every accepted asset/nonce/signature string denotes exactly one on-chain object.
- Expected Immunefi impact: High - signature bound to the wrong contract, signer or nonce (HackenProof: intent signing and verification, nonce management)
- Fast validation: vitest: table-driven parse tests with the listed inputs; assert throws or canonical output.
