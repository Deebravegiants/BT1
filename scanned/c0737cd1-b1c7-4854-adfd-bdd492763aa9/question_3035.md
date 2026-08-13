# Q3035: asset sources auto-approve confusion via AssetSources

## Question
Can an unprivileged attacker connect through website-origin permission or account-exposure flow during normal wallet connection and manipulate `assetName`, `port`, and request ordering so that `AssetSources` in `features/asset-sources/module/asset-sources.ts` make canonicalization or coercion collapse two distinct origin/account identities into one permission bucket, breaking the invariant that string coercion or host normalization must not merge distinct authorities or accounts into one authorization context, and leading to `Sitewide disruption of core services`?

## Target
- File/function: features/asset-sources/module/asset-sources.ts::AssetSources
- Entrypoint: website-origin permission or account-exposure flow during normal wallet connection
- Attacker controls: a request that mixes canonical and non-canonical origin forms, ports, or host spellings
- Exploit idea: make canonicalization or coercion collapse two distinct origin/account identities into one permission bucket
- Invariant to test: string coercion or host normalization must not merge distinct authorities or accounts into one authorization context
- Expected Immunefi impact: Sitewide disruption of core services
- Fast validation: unit-test canonical and non-canonical origin forms and verify they never share trust or auto-approve state unexpectedly
