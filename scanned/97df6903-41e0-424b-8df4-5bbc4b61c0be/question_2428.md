# Q2428: address provider cross-account key exposure via #getSinglesigAddress

## Question
Can an unprivileged attacker connect through receive-address or default-address request from a connected dapp or wallet UI action and manipulate `account`, `origin`, and request ordering so that `#getSinglesigAddress` in `features/address-provider/module/address-provider.js` grow the approved asset/account scope beyond what the user actually authorized, breaking the invariant that addresses, xpubs, and public keys must only be returned for the exact approved account and asset scope, and leading to `Changing sensitive details of other users (including modifying browser local storage) with up to one click of user interaction`?

## Target
- File/function: features/address-provider/module/address-provider.js::#getSinglesigAddress
- Entrypoint: receive-address or default-address request from a connected dapp or wallet UI action
- Attacker controls: cached permission state around untrust, favorite, disable, or account-switch flows
- Exploit idea: grow the approved asset/account scope beyond what the user actually authorized
- Invariant to test: addresses, xpubs, and public keys must only be returned for the exact approved account and asset scope
- Expected Immunefi impact: Changing sensitive details of other users (including modifying browser local storage) with up to one click of user interaction
- Fast validation: rotate the seed or switch active accounts after caching addresses or keys and assert stale cache entries are rejected or invalidated
