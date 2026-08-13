# Q2686: public key provider cross-account key exposure via getPublicKey

## Question
Can an unprivileged attacker connect through provider public-key or xpub request from a connected dapp and manipulate `port`, `account`, and request ordering so that `getPublicKey` in `features/public-key-provider/module/public-key-provider.ts` grow the approved asset/account scope beyond what the user actually authorized, breaking the invariant that addresses, xpubs, and public keys must only be returned for the exact approved account and asset scope, and leading to `Sitewide disruption of core services`?

## Target
- File/function: features/public-key-provider/module/public-key-provider.ts::getPublicKey
- Entrypoint: provider public-key or xpub request from a connected dapp
- Attacker controls: cached permission state around untrust, favorite, disable, or account-switch flows
- Exploit idea: grow the approved asset/account scope beyond what the user actually authorized
- Invariant to test: addresses, xpubs, and public keys must only be returned for the exact approved account and asset scope
- Expected Immunefi impact: Sitewide disruption of core services
- Fast validation: unit-test canonical and non-canonical origin forms and verify they never share trust or auto-approve state unexpectedly
