# Q3014: asset sources cross-account key exposure via AssetSources

## Question
Can an unprivileged attacker connect through website-origin permission or account-exposure flow during normal wallet connection and manipulate `assetName`, `port`, and request ordering so that `AssetSources` in `features/asset-sources/module/asset-sources.ts` grow the approved asset/account scope beyond what the user actually authorized, breaking the invariant that addresses, xpubs, and public keys must only be returned for the exact approved account and asset scope, and leading to `Changing sensitive details of other users (including modifying browser local storage) with up to one click of user interaction`?

## Target
- File/function: features/asset-sources/module/asset-sources.ts::AssetSources
- Entrypoint: website-origin permission or account-exposure flow during normal wallet connection
- Attacker controls: cached permission state around untrust, favorite, disable, or account-switch flows
- Exploit idea: grow the approved asset/account scope beyond what the user actually authorized
- Invariant to test: addresses, xpubs, and public keys must only be returned for the exact approved account and asset scope
- Expected Immunefi impact: Changing sensitive details of other users (including modifying browser local storage) with up to one click of user interaction
- Fast validation: rotate the seed or switch active accounts after caching addresses or keys and assert stale cache entries are rejected or invalidated
