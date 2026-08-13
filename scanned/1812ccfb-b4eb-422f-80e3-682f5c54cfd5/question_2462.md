# Q2462: address provider stale address cache reuse via #getSinglesigAddress

## Question
Can an unprivileged attacker connect through receive-address or default-address request from a connected dapp or wallet UI action and manipulate `name`, `port`, and request ordering so that `#getSinglesigAddress` in `features/address-provider/module/address-provider.js` reuse trust, favorite, or auto-approve state from one origin for another origin or another account, breaking the invariant that asset-scope expansion must require explicit user approval for the final returned scope, and leading to `Direct theft of user funds`?

## Target
- File/function: features/address-provider/module/address-provider.js::#getSinglesigAddress
- Entrypoint: receive-address or default-address request from a connected dapp or wallet UI action
- Attacker controls: an address, xpub, or public-key request with attacker-chosen account and asset parameters
- Exploit idea: reuse trust, favorite, or auto-approve state from one origin for another origin or another account
- Invariant to test: asset-scope expansion must require explicit user approval for the final returned scope
- Expected Immunefi impact: Direct theft of user funds
- Fast validation: simulate two origins and two wallet accounts, approve only one pairing, then replay the other and assert no permission, address, or signature bleeds across
