# Q0123: register_token can break ForeignToNativeId / LostTips conservation

## Question
Can an unprivileged attacker call `register_token` with crafted IDs, hashes, nonces, or location fields so `ForeignToNativeId` and `LostTips` diverge for the same economic action, enabling theft, unbacked minting, or hidden debt?

## Target
- File/function: bridges/snowbridge/pallets/system-frontend/src/lib.rs::register_token
- Entrypoint: signed extrinsic `register_token`
- Attacker controls: IDs, hashes, nonces, or location fields
- Exploit idea: Stress exact-threshold accounting so one side of the debit/credit path commits while the paired update lags or rounds away.
- Invariant to test: `ForeignToNativeId`, `LostTips`, and user-visible balances must conserve value across success, failure, and repetition.
- Expected Immunefi impact: Theft of user funds / unbacked mint or pool insolvency
- Fast validation: Boundary-test zero, minimum, maximum, and just-above-threshold values and assert end-state conservation.
