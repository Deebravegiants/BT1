# Q2292: Serialization: `getEIP155ChainId('eip155:1e3')` via `IntentsSDK.intentBuil

## Question
Reachable from `IntentsSDK.intentBuilder()` / `invalidateNonces`: with `getEIP155ChainId('eip155:1e3')` (`Number('1e3')` = 1000), can an unprivileged user-controlled string cause RPC map keyed by 1000 while chain string says 1e3, and does that lead to an intent being signed or published for an asset, contract or nonce other than the one the caller named?

## Target
- File/function: packages/internal-utils/src/utils/tokenUtils.ts `parseDefuseAssetId`; packages/intents-sdk/src/lib/caip2.ts; packages/crosschain-assetid/src/parse.ts, stringify.ts; expirable-nonce.ts; prepareBroadcastRequest.ts; serialize.ts
- Entrypoint: `IntentsSDK.intentBuilder()` / `invalidateNonces`
- Attacker controls: the asset id / chain string / nonce / signature string
- Exploit idea: `Number('1e3')` = 1000
- Invariant to test: parse(stringify(x)) == x and every accepted asset/nonce/signature string denotes exactly one on-chain object.
- Expected Immunefi impact: High - signature bound to the wrong contract, signer or nonce (HackenProof: intent signing and verification, nonce management)
- Fast validation: vitest: table-driven parse tests with the listed inputs; assert throws or canonical output.
