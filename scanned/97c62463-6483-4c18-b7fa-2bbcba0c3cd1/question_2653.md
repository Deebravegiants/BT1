# Q2653: public key provider origin canonicalization bleed via #getCachedPublicKey

## Question
Can an unprivileged attacker connect through provider public-key or xpub request from a connected dapp and manipulate `keyIdentifier`, `name`, and request ordering so that `#getCachedPublicKey` in `features/public-key-provider/module/public-key-provider.ts` return addresses, xpubs, or public keys from a different account than the one selected by the user, breaking the invariant that untrust, disable, restore, and seed-rotation events must invalidate stale permission and cache state, and leading to `Changing sensitive details of other users (including modifying browser local storage) with up to one click of user interaction`?

## Target
- File/function: features/public-key-provider/module/public-key-provider.ts::#getCachedPublicKey
- Entrypoint: provider public-key or xpub request from a connected dapp
- Attacker controls: two visually similar origins, account selectors, asset lists, and reconnect timing
- Exploit idea: return addresses, xpubs, or public keys from a different account than the one selected by the user
- Invariant to test: untrust, disable, restore, and seed-rotation events must invalidate stale permission and cache state
- Expected Immunefi impact: Changing sensitive details of other users (including modifying browser local storage) with up to one click of user interaction
- Fast validation: rotate the seed or switch active accounts after caching addresses or keys and assert stale cache entries are rejected or invalidated
