# Q3093: utils stale address cache reuse via getSupportedPurposes

## Question
Can an unprivileged attacker connect through website-origin permission or account-exposure flow during normal wallet connection and manipulate `port`, `account`, and request ordering so that `getSupportedPurposes` in `features/asset-sources/module/utils.ts` reuse trust, favorite, or auto-approve state from one origin for another origin or another account, breaking the invariant that asset-scope expansion must require explicit user approval for the final returned scope, and leading to `Sitewide disruption of core services`?

## Target
- File/function: features/asset-sources/module/utils.ts::getSupportedPurposes
- Entrypoint: website-origin permission or account-exposure flow during normal wallet connection
- Attacker controls: an address, xpub, or public-key request with attacker-chosen account and asset parameters
- Exploit idea: reuse trust, favorite, or auto-approve state from one origin for another origin or another account
- Invariant to test: asset-scope expansion must require explicit user approval for the final returned scope
- Expected Immunefi impact: Sitewide disruption of core services
- Fast validation: unit-test canonical and non-canonical origin forms and verify they never share trust or auto-approve state unexpectedly
