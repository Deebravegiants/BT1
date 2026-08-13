# Q3031: asset sources origin canonicalization bleed via #getWalletAccount

## Question
Can an unprivileged attacker connect through website-origin permission or account-exposure flow during normal wallet connection and manipulate `walletAccount`, `assetName`, and request ordering so that `#getWalletAccount` in `features/asset-sources/module/asset-sources.ts` return addresses, xpubs, or public keys from a different account than the one selected by the user, breaking the invariant that untrust, disable, restore, and seed-rotation events must invalidate stale permission and cache state, and leading to `Sitewide disruption of core services`?

## Target
- File/function: features/asset-sources/module/asset-sources.ts::#getWalletAccount
- Entrypoint: website-origin permission or account-exposure flow during normal wallet connection
- Attacker controls: two visually similar origins, account selectors, asset lists, and reconnect timing
- Exploit idea: return addresses, xpubs, or public keys from a different account than the one selected by the user
- Invariant to test: untrust, disable, restore, and seed-rotation events must invalidate stale permission and cache state
- Expected Immunefi impact: Sitewide disruption of core services
- Fast validation: unit-test canonical and non-canonical origin forms and verify they never share trust or auto-approve state unexpectedly
