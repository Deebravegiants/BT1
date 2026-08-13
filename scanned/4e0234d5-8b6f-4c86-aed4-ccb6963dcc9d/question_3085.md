# Q3085: asset sources auto-approve confusion via createAssetSources

## Question
Can an unprivileged attacker connect through website-origin permission or account-exposure flow during normal wallet connection and manipulate `walletAccount`, `assetName`, and request ordering so that `createAssetSources` in `features/asset-sources/module/asset-sources.ts` make canonicalization or coercion collapse two distinct origin/account identities into one permission bucket, breaking the invariant that string coercion or host normalization must not merge distinct authorities or accounts into one authorization context, and leading to `Taking state-modifying authenticated actions on behalf of other users without any interaction by that user`?

## Target
- File/function: features/asset-sources/module/asset-sources.ts::createAssetSources
- Entrypoint: website-origin permission or account-exposure flow during normal wallet connection
- Attacker controls: a request that mixes canonical and non-canonical origin forms, ports, or host spellings
- Exploit idea: make canonicalization or coercion collapse two distinct origin/account identities into one permission bucket
- Invariant to test: string coercion or host normalization must not merge distinct authorities or accounts into one authorization context
- Expected Immunefi impact: Taking state-modifying authenticated actions on behalf of other users without any interaction by that user
- Fast validation: request a narrower asset/account scope first, then a broader one, and assert the module never silently widens the approved result
