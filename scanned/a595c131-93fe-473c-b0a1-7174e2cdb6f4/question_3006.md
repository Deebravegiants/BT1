# Q3006: asset sources origin canonicalization bleed via isSupported

## Question
Can an unprivileged attacker connect through website-origin permission or account-exposure flow during normal wallet connection and manipulate `port`, `walletAccount`, and request ordering so that `isSupported` in `features/asset-sources/module/asset-sources.ts` return addresses, xpubs, or public keys from a different account than the one selected by the user, breaking the invariant that untrust, disable, restore, and seed-rotation events must invalidate stale permission and cache state, and leading to `Changing sensitive details of other users (including modifying browser local storage) with up to one click of user interaction`?

## Target
- File/function: features/asset-sources/module/asset-sources.ts::isSupported
- Entrypoint: website-origin permission or account-exposure flow during normal wallet connection
- Attacker controls: two visually similar origins, account selectors, asset lists, and reconnect timing
- Exploit idea: return addresses, xpubs, or public keys from a different account than the one selected by the user
- Invariant to test: untrust, disable, restore, and seed-rotation events must invalidate stale permission and cache state
- Expected Immunefi impact: Changing sensitive details of other users (including modifying browser local storage) with up to one click of user interaction
- Fast validation: rotate the seed or switch active accounts after caching addresses or keys and assert stale cache entries are rejected or invalidated
