# Q2471: known addresses cross-account key exposure via walletAccount

## Question
Can an unprivileged attacker connect through receive-address or default-address request from a connected dapp or wallet UI action and manipulate `walletAccount`, `assetName`, and request ordering so that `walletAccount` in `features/address-provider/module/known-addresses.js` grow the approved asset/account scope beyond what the user actually authorized, breaking the invariant that addresses, xpubs, and public keys must only be returned for the exact approved account and asset scope, and leading to `Direct theft of user funds`?

## Target
- File/function: features/address-provider/module/known-addresses.js::walletAccount
- Entrypoint: receive-address or default-address request from a connected dapp or wallet UI action
- Attacker controls: cached permission state around untrust, favorite, disable, or account-switch flows
- Exploit idea: grow the approved asset/account scope beyond what the user actually authorized
- Invariant to test: addresses, xpubs, and public keys must only be returned for the exact approved account and asset scope
- Expected Immunefi impact: Direct theft of user funds
- Fast validation: simulate two origins and two wallet accounts, approve only one pairing, then replay the other and assert no permission, address, or signature bleeds across
