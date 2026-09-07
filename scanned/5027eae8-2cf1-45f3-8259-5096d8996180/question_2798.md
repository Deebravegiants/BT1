# Q2798: Serialization: `parse1cs('1cs_v1:eth:erc20:%2e%2e')` via `IntentsSDK.intentBuil

## Question
Reachable from `IntentsSDK.intentBuilder()` / `invalidateNonces`: with `parse1cs('1cs_v1:eth:erc20:%2e%2e')` (`decodeURIComponent` on reference), can an unprivileged user-controlled string cause path-like references in asset registries, and does that lead to an intent being signed or published for an asset, contract or nonce other than the one the caller named?

## Target
- File/function: packages/internal-utils/src/utils/tokenUtils.ts `parseDefuseAssetId`; packages/intents-sdk/src/lib/caip2.ts; packages/crosschain-assetid/src/parse.ts, stringify.ts; expirable-nonce.ts; prepareBroadcastRequest.ts; serialize.ts
- Entrypoint: `IntentsSDK.intentBuilder()` / `invalidateNonces`
- Attacker controls: the asset id / chain string / nonce / signature string
- Exploit idea: `decodeURIComponent` on reference
- Invariant to test: parse(stringify(x)) == x and every accepted asset/nonce/signature string denotes exactly one on-chain object.
- Expected Immunefi impact: High - signature bound to the wrong contract, signer or nonce (HackenProof: intent signing and verification, nonce management)
- Fast validation: vitest: table-driven parse tests with the listed inputs; assert throws or canonical output.
