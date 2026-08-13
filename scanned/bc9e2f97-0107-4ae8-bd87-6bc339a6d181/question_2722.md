# Q2722: legacy permission scope widening via clone

## Question
Can an unprivileged attacker connect through provider public-key or xpub request from a connected dapp and manipulate `walletAccount`, `assetName`, and request ordering so that `clone` in `features/public-key-provider/module/store/formats/storage/legacy.ts` keep stale connected-account or address-cache data alive across seed rotation, restore, or account changes, breaking the invariant that origin trust and auto-approve state must be keyed by a canonical origin and the intended wallet account, and leading to `Changing sensitive details of other users (including modifying browser local storage) with up to one click of user interaction`?

## Target
- File/function: features/public-key-provider/module/store/formats/storage/legacy.ts::clone
- Entrypoint: provider public-key or xpub request from a connected dapp
- Attacker controls: the origin string, wallet-account name, and the sequence of connect / sign / auto-approve actions
- Exploit idea: keep stale connected-account or address-cache data alive across seed rotation, restore, or account changes
- Invariant to test: origin trust and auto-approve state must be keyed by a canonical origin and the intended wallet account
- Expected Immunefi impact: Changing sensitive details of other users (including modifying browser local storage) with up to one click of user interaction
- Fast validation: rotate the seed or switch active accounts after caching addresses or keys and assert stale cache entries are rejected or invalidated
