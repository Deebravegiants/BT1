# Q5055: PoA prefix parse `aleo-.omft.near`

## Question
Can an unprivileged caller pass `assetId` = `nep141:aleo-.omft.near` so that `PoaBridge.parseAssetId` (matching `endsWith('.omft.near')`) and `contractIdToCaip2` (matching `startsWith('aleo.')` or `startsWith('aleo-')`) resolve a chain for a contract that is not a PoA-issued token, causing `validateAddress` to run for chain `aleo` while the `ft_withdraw` targets `aleo-.omft.near` and the PoA relayer never pays out?

## Target
- File/function: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge-utils.ts `contractIdToCaip2`, `toPoaNetwork`; poa-bridge.ts `parseAssetId`, `supports`
- Entrypoint: `IntentsSDK.parseAssetId` / `processWithdrawal`
- Attacker controls: `assetId` = `nep141:aleo-.omft.near`
- Exploit idea: Prefix matching is by `startsWith` over a fixed table and factory suffix only; sub-accounts and look-alike ids under the factory can satisfy both tests. `getCachedSupportedTokens` is consulted only in `validateWithdrawal`, by `intents_token_id` equality.
- Invariant to test: parseAssetId(assetId).blockchain must equal the origin chain of a token actually issued by `omft.near` for that id; unknown ids must throw `UnsupportedAssetIdError`.
- Expected Immunefi impact: High - withdrawal stuck or refunded to the wrong account until manual intervention (HackenProof: withdrawal processing; Immunefi class: temporary freezing of funds)
- Fast validation: vitest: `new PoaBridge(...).parseAssetId('nep141:aleo-.omft.near')` and `supports()`; mock `supported_tokens` to exclude it and assert `validateWithdrawal` rejects.
