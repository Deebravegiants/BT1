# Q3081: asset sources origin canonicalization bleed via getSupportedPurposes

## Question
Can an unprivileged attacker connect through website-origin permission or account-exposure flow during normal wallet connection and manipulate `port`, `walletAccount`, and request ordering so that `getSupportedPurposes` in `features/asset-sources/module/asset-sources.ts` return addresses, xpubs, or public keys from a different account than the one selected by the user, breaking the invariant that untrust, disable, restore, and seed-rotation events must invalidate stale permission and cache state, and leading to `Taking state-modifying authenticated actions on behalf of other users without any interaction by that user`?

## Target
- File/function: features/asset-sources/module/asset-sources.ts::getSupportedPurposes
- Entrypoint: website-origin permission or account-exposure flow during normal wallet connection
- Attacker controls: two visually similar origins, account selectors, asset lists, and reconnect timing
- Exploit idea: return addresses, xpubs, or public keys from a different account than the one selected by the user
- Invariant to test: untrust, disable, restore, and seed-rotation events must invalidate stale permission and cache state
- Expected Immunefi impact: Taking state-modifying authenticated actions on behalf of other users without any interaction by that user
- Fast validation: request a narrower asset/account scope first, then a broader one, and assert the module never silently widens the approved result
