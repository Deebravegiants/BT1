# Q2516: known addresses cross-account key exposure via getCacheKey

## Question
Can an unprivileged attacker connect through receive-address or default-address request from a connected dapp or wallet UI action and manipulate `walletAccount`, `assetName`, and request ordering so that `getCacheKey` in `features/address-provider/module/known-addresses.js` grow the approved asset/account scope beyond what the user actually authorized, breaking the invariant that addresses, xpubs, and public keys must only be returned for the exact approved account and asset scope, and leading to `Taking state-modifying authenticated actions on behalf of other users without any interaction by that user`?

## Target
- File/function: features/address-provider/module/known-addresses.js::getCacheKey
- Entrypoint: receive-address or default-address request from a connected dapp or wallet UI action
- Attacker controls: cached permission state around untrust, favorite, disable, or account-switch flows
- Exploit idea: grow the approved asset/account scope beyond what the user actually authorized
- Invariant to test: addresses, xpubs, and public keys must only be returned for the exact approved account and asset scope
- Expected Immunefi impact: Taking state-modifying authenticated actions on behalf of other users without any interaction by that user
- Fast validation: request a narrower asset/account scope first, then a broader one, and assert the module never silently widens the approved result
