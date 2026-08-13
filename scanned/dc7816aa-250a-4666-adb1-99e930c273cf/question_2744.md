# Q2744: legacy cross-account key exposure via StorageFormatLegacyBuilder

## Question
Can an unprivileged attacker connect through provider public-key or xpub request from a connected dapp and manipulate `port`, `origin`, and request ordering so that `StorageFormatLegacyBuilder` in `features/public-key-provider/module/store/formats/storage/legacy.ts` grow the approved asset/account scope beyond what the user actually authorized, breaking the invariant that addresses, xpubs, and public keys must only be returned for the exact approved account and asset scope, and leading to `Direct theft of user funds`?

## Target
- File/function: features/public-key-provider/module/store/formats/storage/legacy.ts::StorageFormatLegacyBuilder
- Entrypoint: provider public-key or xpub request from a connected dapp
- Attacker controls: cached permission state around untrust, favorite, disable, or account-switch flows
- Exploit idea: grow the approved asset/account scope beyond what the user actually authorized
- Invariant to test: addresses, xpubs, and public keys must only be returned for the exact approved account and asset scope
- Expected Immunefi impact: Direct theft of user funds
- Fast validation: simulate two origins and two wallet accounts, approve only one pairing, then replay the other and assert no permission, address, or signature bleeds across
