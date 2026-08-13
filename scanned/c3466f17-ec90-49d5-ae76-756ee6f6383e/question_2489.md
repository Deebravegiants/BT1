# Q2489: known addresses permission scope widening via walletAccount

## Question
Can an unprivileged attacker connect through receive-address or default-address request from a connected dapp or wallet UI action and manipulate `walletAccount`, `assetName`, and request ordering so that `walletAccount` in `features/address-provider/module/known-addresses.js` keep stale connected-account or address-cache data alive across seed rotation, restore, or account changes, breaking the invariant that origin trust and auto-approve state must be keyed by a canonical origin and the intended wallet account, and leading to `Changing sensitive details of other users (including modifying browser local storage) with up to one click of user interaction`?

## Target
- File/function: features/address-provider/module/known-addresses.js::walletAccount
- Entrypoint: receive-address or default-address request from a connected dapp or wallet UI action
- Attacker controls: the origin string, wallet-account name, and the sequence of connect / sign / auto-approve actions
- Exploit idea: keep stale connected-account or address-cache data alive across seed rotation, restore, or account changes
- Invariant to test: origin trust and auto-approve state must be keyed by a canonical origin and the intended wallet account
- Expected Immunefi impact: Changing sensitive details of other users (including modifying browser local storage) with up to one click of user interaction
- Fast validation: rotate the seed or switch active accounts after caching addresses or keys and assert stale cache entries are rejected or invalidated
