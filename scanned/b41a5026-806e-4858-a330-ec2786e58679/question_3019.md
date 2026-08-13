# Q3019: asset sources cross-account key exposure via getDefaultPurpose

## Question
Can an unprivileged attacker connect through website-origin permission or account-exposure flow during normal wallet connection and manipulate `walletAccount`, `assetName`, and request ordering so that `getDefaultPurpose` in `features/asset-sources/module/asset-sources.ts` grow the approved asset/account scope beyond what the user actually authorized, breaking the invariant that addresses, xpubs, and public keys must only be returned for the exact approved account and asset scope, and leading to `Sitewide disruption of core services`?

## Target
- File/function: features/asset-sources/module/asset-sources.ts::getDefaultPurpose
- Entrypoint: website-origin permission or account-exposure flow during normal wallet connection
- Attacker controls: cached permission state around untrust, favorite, disable, or account-switch flows
- Exploit idea: grow the approved asset/account scope beyond what the user actually authorized
- Invariant to test: addresses, xpubs, and public keys must only be returned for the exact approved account and asset scope
- Expected Immunefi impact: Sitewide disruption of core services
- Fast validation: unit-test canonical and non-canonical origin forms and verify they never share trust or auto-approve state unexpectedly
