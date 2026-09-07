# Q4326: Serialization: `transformERC191Signature` on a signature wi via `IntentsSDK.intentBuil

## Question
Reachable from `IntentsSDK.intentBuilder()` / `invalidateNonces`: with `transformERC191Signature` on a signature with v = 0x1b/0x1c vs 0/1 vs 27/28 encoded as 2 hex chars (`toRecoveryBit` throws on other values), can an unprivileged user-controlled string cause signature from a wallet returning 65-byte with v=0x00 works; check `secp256k1:` base58 length, and does that lead to an intent being signed or published for an asset, contract or nonce other than the one the caller named?

## Target
- File/function: packages/internal-utils/src/utils/tokenUtils.ts `parseDefuseAssetId`; packages/intents-sdk/src/lib/caip2.ts; packages/crosschain-assetid/src/parse.ts, stringify.ts; expirable-nonce.ts; prepareBroadcastRequest.ts; serialize.ts
- Entrypoint: `IntentsSDK.intentBuilder()` / `invalidateNonces`
- Attacker controls: the asset id / chain string / nonce / signature string
- Exploit idea: `toRecoveryBit` throws on other values
- Invariant to test: parse(stringify(x)) == x and every accepted asset/nonce/signature string denotes exactly one on-chain object.
- Expected Immunefi impact: High - signature bound to the wrong contract, signer or nonce (HackenProof: intent signing and verification, nonce management)
- Fast validation: vitest: table-driven parse tests with the listed inputs; assert throws or canonical output.
