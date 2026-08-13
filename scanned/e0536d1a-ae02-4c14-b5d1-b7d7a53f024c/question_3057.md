# Q3057: asset sources permission scope widening via createAssetSources

## Question
Can an unprivileged attacker connect through website-origin permission or account-exposure flow during normal wallet connection and manipulate `port`, `walletAccount`, and request ordering so that `createAssetSources` in `features/asset-sources/module/asset-sources.ts` keep stale connected-account or address-cache data alive across seed rotation, restore, or account changes, breaking the invariant that origin trust and auto-approve state must be keyed by a canonical origin and the intended wallet account, and leading to `Taking state-modifying authenticated actions on behalf of other users without any interaction by that user`?

## Target
- File/function: features/asset-sources/module/asset-sources.ts::createAssetSources
- Entrypoint: website-origin permission or account-exposure flow during normal wallet connection
- Attacker controls: the origin string, wallet-account name, and the sequence of connect / sign / auto-approve actions
- Exploit idea: keep stale connected-account or address-cache data alive across seed rotation, restore, or account changes
- Invariant to test: origin trust and auto-approve state must be keyed by a canonical origin and the intended wallet account
- Expected Immunefi impact: Taking state-modifying authenticated actions on behalf of other users without any interaction by that user
- Fast validation: request a narrower asset/account scope first, then a broader one, and assert the module never silently widens the approved result
