# Q3267: PoA supported_tokens Berachain: the token appears under a different `cha

## Question
For a PoA withdrawal on Berachain, when the `supported_tokens` entry has the token appears under a different `chain` key than `toPoaNetwork` produced, so `tokenInfo == null` and `UnsupportedAssetIdError` fires only at validate time, does `PoaBridge.validateWithdrawal` skip the destination==token block or the minimum check, so an unprivileged user can sign a withdrawal that the PoA relayer will never pay (or pays to the token contract), while intents.near has already burned the omft token?

## Target
- File/function: packages/intents-sdk/src/bridges/poa-bridge/poa-bridge.ts `validateWithdrawal`, `getCachedSupportedTokens`; poa-bridge-utils.ts `toPoaNetwork`
- Entrypoint: `IntentsSDK.processWithdrawal`
- Attacker controls: `assetId`, `destinationAddress`, timing vs 30s cache
- Exploit idea: The guard depends on fields of an external list; `native` short-circuits the address comparison and `'0'` minimum disables the floor.
- Invariant to test: for every accepted (assetId, destination) the PoA bridge will pay destination and destination != token contract.
- Expected Immunefi impact: High - withdrawal stuck or refunded to the wrong account until manual intervention (HackenProof: withdrawal processing; Immunefi class: temporary freezing of funds)
- Fast validation: vitest: mock `supported_tokens` variants; assert throws.
