# Q3076: asset sources origin canonicalization bleed via isSupported

## Question
Can an unprivileged attacker connect through website-origin permission or account-exposure flow during normal wallet connection and manipulate `walletAccount`, `assetName`, and request ordering so that `isSupported` in `features/asset-sources/module/asset-sources.ts` return addresses, xpubs, or public keys from a different account than the one selected by the user, breaking the invariant that untrust, disable, restore, and seed-rotation events must invalidate stale permission and cache state, and leading to `Direct theft of user funds`?

## Target
- File/function: features/asset-sources/module/asset-sources.ts::isSupported
- Entrypoint: website-origin permission or account-exposure flow during normal wallet connection
- Attacker controls: two visually similar origins, account selectors, asset lists, and reconnect timing
- Exploit idea: return addresses, xpubs, or public keys from a different account than the one selected by the user
- Invariant to test: untrust, disable, restore, and seed-rotation events must invalidate stale permission and cache state
- Expected Immunefi impact: Direct theft of user funds
- Fast validation: simulate two origins and two wallet accounts, approve only one pairing, then replay the other and assert no permission, address, or signature bleeds across
