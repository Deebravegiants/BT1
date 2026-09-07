# Q1444: Serialization: `parseDefuseAssetId('NEP141:wrap.near')` via `IntentsSDK.signAndSen

## Question
Reachable from `IntentsSDK.signAndSendIntent` error path: with `parseDefuseAssetId('NEP141:wrap.near')` (standard is case-sensitive, contractId validated by `validateNearAddress`), can an unprivileged user-controlled string cause assert(false) path vs typed error; check `sdk.parseAssetId` swallows into `UnsupportedAssetIdError`, and does that lead to an intent being signed or published for an asset, contract or nonce other than the one the caller named?

## Target
- File/function: packages/internal-utils/src/utils/tokenUtils.ts `parseDefuseAssetId`; packages/intents-sdk/src/lib/caip2.ts; packages/crosschain-assetid/src/parse.ts, stringify.ts; expirable-nonce.ts; prepareBroadcastRequest.ts; serialize.ts
- Entrypoint: `IntentsSDK.signAndSendIntent` error path
- Attacker controls: the asset id / chain string / nonce / signature string
- Exploit idea: standard is case-sensitive, contractId validated by `validateNearAddress`
- Invariant to test: parse(stringify(x)) == x and every accepted asset/nonce/signature string denotes exactly one on-chain object.
- Expected Immunefi impact: High - signature bound to the wrong contract, signer or nonce (HackenProof: intent signing and verification, nonce management)
- Fast validation: vitest: table-driven parse tests with the listed inputs; assert throws or canonical output.
