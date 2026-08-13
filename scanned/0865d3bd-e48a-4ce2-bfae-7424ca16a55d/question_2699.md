# Q2699: public key provider permission scope widening via getExtendedPublicKey

## Question
Can an unprivileged attacker connect through provider public-key or xpub request from a connected dapp and manipulate `seedId`, `publicKey`, and request ordering so that `getExtendedPublicKey` in `features/public-key-provider/module/public-key-provider.ts` keep stale connected-account or address-cache data alive across seed rotation, restore, or account changes, breaking the invariant that origin trust and auto-approve state must be keyed by a canonical origin and the intended wallet account, and leading to `Direct theft of user funds`?

## Target
- File/function: features/public-key-provider/module/public-key-provider.ts::getExtendedPublicKey
- Entrypoint: provider public-key or xpub request from a connected dapp
- Attacker controls: the origin string, wallet-account name, and the sequence of connect / sign / auto-approve actions
- Exploit idea: keep stale connected-account or address-cache data alive across seed rotation, restore, or account changes
- Invariant to test: origin trust and auto-approve state must be keyed by a canonical origin and the intended wallet account
- Expected Immunefi impact: Direct theft of user funds
- Fast validation: simulate two origins and two wallet accounts, approve only one pairing, then replay the other and assert no permission, address, or signature bleeds across
