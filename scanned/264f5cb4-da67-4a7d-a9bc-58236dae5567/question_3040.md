# Q3040: asset sources auto-approve confusion via getDefaultPurpose

## Question
Can an unprivileged attacker connect through website-origin permission or account-exposure flow during normal wallet connection and manipulate `walletAccount`, `assetName`, and request ordering so that `getDefaultPurpose` in `features/asset-sources/module/asset-sources.ts` make canonicalization or coercion collapse two distinct origin/account identities into one permission bucket, breaking the invariant that string coercion or host normalization must not merge distinct authorities or accounts into one authorization context, and leading to `Direct theft of user funds`?

## Target
- File/function: features/asset-sources/module/asset-sources.ts::getDefaultPurpose
- Entrypoint: website-origin permission or account-exposure flow during normal wallet connection
- Attacker controls: a request that mixes canonical and non-canonical origin forms, ports, or host spellings
- Exploit idea: make canonicalization or coercion collapse two distinct origin/account identities into one permission bucket
- Invariant to test: string coercion or host normalization must not merge distinct authorities or accounts into one authorization context
- Expected Immunefi impact: Direct theft of user funds
- Fast validation: simulate two origins and two wallet accounts, approve only one pairing, then replay the other and assert no permission, address, or signature bleeds across
