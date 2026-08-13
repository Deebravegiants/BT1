# Q2127: connections cross-account key exposure via updateConnection

## Question
Can an unprivileged attacker connect through wallet connect / authorize / auto-approve flow from a connected website and manipulate `account`, `connectedAssetName`, and request ordering so that `updateConnection` in `features/connected-origins/module/connections.js` grow the approved asset/account scope beyond what the user actually authorized, breaking the invariant that addresses, xpubs, and public keys must only be returned for the exact approved account and asset scope, and leading to `Sitewide disruption of core services`?

## Target
- File/function: features/connected-origins/module/connections.js::updateConnection
- Entrypoint: wallet connect / authorize / auto-approve flow from a connected website
- Attacker controls: cached permission state around untrust, favorite, disable, or account-switch flows
- Exploit idea: grow the approved asset/account scope beyond what the user actually authorized
- Invariant to test: addresses, xpubs, and public keys must only be returned for the exact approved account and asset scope
- Expected Immunefi impact: Sitewide disruption of core services
- Fast validation: unit-test canonical and non-canonical origin forms and verify they never share trust or auto-approve state unexpectedly
