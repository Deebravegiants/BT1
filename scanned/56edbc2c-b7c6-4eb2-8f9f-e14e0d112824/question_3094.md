# Q3094: utils cross-account key exposure via getDefaultPurpose

## Question
Can an unprivileged attacker connect through website-origin permission or account-exposure flow during normal wallet connection and manipulate `account`, `walletAccount`, and request ordering so that `getDefaultPurpose` in `features/asset-sources/module/utils.ts` grow the approved asset/account scope beyond what the user actually authorized, breaking the invariant that addresses, xpubs, and public keys must only be returned for the exact approved account and asset scope, and leading to `Direct theft of user funds`?

## Target
- File/function: features/asset-sources/module/utils.ts::getDefaultPurpose
- Entrypoint: website-origin permission or account-exposure flow during normal wallet connection
- Attacker controls: cached permission state around untrust, favorite, disable, or account-switch flows
- Exploit idea: grow the approved asset/account scope beyond what the user actually authorized
- Invariant to test: addresses, xpubs, and public keys must only be returned for the exact approved account and asset scope
- Expected Immunefi impact: Direct theft of user funds
- Fast validation: simulate two origins and two wallet accounts, approve only one pairing, then replay the other and assert no permission, address, or signature bleeds across
