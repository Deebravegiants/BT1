# Q2791: index origin canonicalization bleed via validateSerialized

## Question
Can an unprivileged attacker connect through provider public-key or xpub request from a connected dapp and manipulate `publicKey`, `xpub`, and request ordering so that `validateSerialized` in `features/public-key-provider/module/store/formats/serialization/index.ts` return addresses, xpubs, or public keys from a different account than the one selected by the user, breaking the invariant that untrust, disable, restore, and seed-rotation events must invalidate stale permission and cache state, and leading to `Sitewide disruption of core services`?

## Target
- File/function: features/public-key-provider/module/store/formats/serialization/index.ts::validateSerialized
- Entrypoint: provider public-key or xpub request from a connected dapp
- Attacker controls: two visually similar origins, account selectors, asset lists, and reconnect timing
- Exploit idea: return addresses, xpubs, or public keys from a different account than the one selected by the user
- Invariant to test: untrust, disable, restore, and seed-rotation events must invalidate stale permission and cache state
- Expected Immunefi impact: Sitewide disruption of core services
- Fast validation: unit-test canonical and non-canonical origin forms and verify they never share trust or auto-approve state unexpectedly
