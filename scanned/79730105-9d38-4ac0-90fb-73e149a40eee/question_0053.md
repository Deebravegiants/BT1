# Q0053: set_reserves can break AssetDetails / Accounts conservation

## Question
Can an unprivileged attacker call `set_reserves` with crafted IDs, hashes, nonces, or location fields, duplicate or adversarial list ordering so `AssetDetails` and `Accounts` diverge for the same economic action, enabling theft, unbacked minting, or hidden debt?

## Target
- File/function: substrate/frame/assets/src/lib.rs::set_reserves
- Entrypoint: signed extrinsic `set_reserves`
- Attacker controls: IDs, hashes, nonces, or location fields, duplicate or adversarial list ordering
- Exploit idea: Stress exact-threshold accounting so one side of the debit/credit path commits while the paired update lags or rounds away.
- Invariant to test: `AssetDetails`, `Accounts`, and user-visible balances must conserve value across success, failure, and repetition.
- Expected Immunefi impact: Theft of user funds / unbacked mint or pool insolvency
- Fast validation: Boundary-test zero, minimum, maximum, and just-above-threshold values and assert end-state conservation.
