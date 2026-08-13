# Q2367: utils origin canonicalization bleed via diffCaches

## Question
Can an unprivileged attacker connect through receive-address or default-address request from a connected dapp or wallet UI action and manipulate `assetName`, `derivationPath`, and request ordering so that `diffCaches` in `features/address-provider/module/address-cache/utils.js` return addresses, xpubs, or public keys from a different account than the one selected by the user, breaking the invariant that untrust, disable, restore, and seed-rotation events must invalidate stale permission and cache state, and leading to `Changing sensitive details of other users (including modifying browser local storage) with up to one click of user interaction`?

## Target
- File/function: features/address-provider/module/address-cache/utils.js::diffCaches
- Entrypoint: receive-address or default-address request from a connected dapp or wallet UI action
- Attacker controls: two visually similar origins, account selectors, asset lists, and reconnect timing
- Exploit idea: return addresses, xpubs, or public keys from a different account than the one selected by the user
- Invariant to test: untrust, disable, restore, and seed-rotation events must invalidate stale permission and cache state
- Expected Immunefi impact: Changing sensitive details of other users (including modifying browser local storage) with up to one click of user interaction
- Fast validation: rotate the seed or switch active accounts after caching addresses or keys and assert stale cache entries are rejected or invalidated
