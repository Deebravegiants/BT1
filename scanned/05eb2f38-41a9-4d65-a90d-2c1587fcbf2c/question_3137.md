# Q3137: Serialization: `stringify1cs` round trip with `:` inside re via `IntentsSDK.parseAsset

## Question
Reachable from `IntentsSDK.parseAssetId` / `createWithdrawalIntents`: with `stringify1cs` round trip with `:` inside reference (`encodeURIComponent` encodes ':' but `parse1cs` splits on ':' first), can an unprivileged user-controlled string cause asymmetric parse of selectors, and does that lead to an intent being signed or published for an asset, contract or nonce other than the one the caller named?

## Target
- File/function: packages/internal-utils/src/utils/tokenUtils.ts `parseDefuseAssetId`; packages/intents-sdk/src/lib/caip2.ts; packages/crosschain-assetid/src/parse.ts, stringify.ts; expirable-nonce.ts; prepareBroadcastRequest.ts; serialize.ts
- Entrypoint: `IntentsSDK.parseAssetId` / `createWithdrawalIntents`
- Attacker controls: the asset id / chain string / nonce / signature string
- Exploit idea: `encodeURIComponent` encodes ':' but `parse1cs` splits on ':' first
- Invariant to test: parse(stringify(x)) == x and every accepted asset/nonce/signature string denotes exactly one on-chain object.
- Expected Immunefi impact: High - signature bound to the wrong contract, signer or nonce (HackenProof: intent signing and verification, nonce management)
- Fast validation: vitest: table-driven parse tests with the listed inputs; assert throws or canonical output.
