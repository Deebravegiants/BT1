# Q3047: asset sources permission scope widening via getDefaultPurpose

## Question
Can an unprivileged attacker connect through website-origin permission or account-exposure flow during normal wallet connection and manipulate `assetName`, `port`, and request ordering so that `getDefaultPurpose` in `features/asset-sources/module/asset-sources.ts` keep stale connected-account or address-cache data alive across seed rotation, restore, or account changes, breaking the invariant that origin trust and auto-approve state must be keyed by a canonical origin and the intended wallet account, and leading to `Sitewide disruption of core services`?

## Target
- File/function: features/asset-sources/module/asset-sources.ts::getDefaultPurpose
- Entrypoint: website-origin permission or account-exposure flow during normal wallet connection
- Attacker controls: the origin string, wallet-account name, and the sequence of connect / sign / auto-approve actions
- Exploit idea: keep stale connected-account or address-cache data alive across seed rotation, restore, or account changes
- Invariant to test: origin trust and auto-approve state must be keyed by a canonical origin and the intended wallet account
- Expected Immunefi impact: Sitewide disruption of core services
- Fast validation: unit-test canonical and non-canonical origin forms and verify they never share trust or auto-approve state unexpectedly
