# Q0931: Serialization: `parseDefuseAssetId('nep245:v2_1.omni.hot.tg via `IntentsSDK.signAndSen

## Question
Reachable from `IntentsSDK.signAndSendIntent` error path: with `parseDefuseAssetId('nep245:v2_1.omni.hot.tg:')` (empty tokenId passes `multiTokenId != null`), can an unprivileged user-controlled string cause HOT parse yields chainId '' -> `hotNetworkIdToCAIP2('')` throws inside try -> `UnsupportedAssetIdError` vs silent null, and does that lead to an intent being signed or published for an asset, contract or nonce other than the one the caller named?

## Target
- File/function: packages/internal-utils/src/utils/tokenUtils.ts `parseDefuseAssetId`; packages/intents-sdk/src/lib/caip2.ts; packages/crosschain-assetid/src/parse.ts, stringify.ts; expirable-nonce.ts; prepareBroadcastRequest.ts; serialize.ts
- Entrypoint: `IntentsSDK.signAndSendIntent` error path
- Attacker controls: the asset id / chain string / nonce / signature string
- Exploit idea: empty tokenId passes `multiTokenId != null`
- Invariant to test: parse(stringify(x)) == x and every accepted asset/nonce/signature string denotes exactly one on-chain object.
- Expected Immunefi impact: High - signature bound to the wrong contract, signer or nonce (HackenProof: intent signing and verification, nonce management)
- Fast validation: vitest: table-driven parse tests with the listed inputs; assert throws or canonical output.
