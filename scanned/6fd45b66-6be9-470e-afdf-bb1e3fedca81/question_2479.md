# Q2479: known addresses permission scope widening via KnownAddresses

## Question
Can an unprivileged attacker connect through receive-address or default-address request from a connected dapp or wallet UI action and manipulate `port`, `walletAccount`, and request ordering so that `KnownAddresses` in `features/address-provider/module/known-addresses.js` keep stale connected-account or address-cache data alive across seed rotation, restore, or account changes, breaking the invariant that origin trust and auto-approve state must be keyed by a canonical origin and the intended wallet account, and leading to `Direct theft of user funds`?

## Target
- File/function: features/address-provider/module/known-addresses.js::KnownAddresses
- Entrypoint: receive-address or default-address request from a connected dapp or wallet UI action
- Attacker controls: the origin string, wallet-account name, and the sequence of connect / sign / auto-approve actions
- Exploit idea: keep stale connected-account or address-cache data alive across seed rotation, restore, or account changes
- Invariant to test: origin trust and auto-approve state must be keyed by a canonical origin and the intended wallet account
- Expected Immunefi impact: Direct theft of user funds
- Fast validation: simulate two origins and two wallet accounts, approve only one pairing, then replay the other and assert no permission, address, or signature bleeds across
