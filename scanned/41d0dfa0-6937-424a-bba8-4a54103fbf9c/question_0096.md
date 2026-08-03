# Q0096: poke_deposit can break Accounts / index ownership conservation

## Question
Can an unprivileged attacker call `poke_deposit` with crafted IDs, hashes, nonces, or location fields so `Accounts` and `index ownership` diverge for the same economic action, enabling theft, unbacked minting, or hidden debt?

## Target
- File/function: substrate/frame/indices/src/lib.rs::poke_deposit
- Entrypoint: signed extrinsic `poke_deposit`
- Attacker controls: IDs, hashes, nonces, or location fields
- Exploit idea: Stress exact-threshold accounting so one side of the debit/credit path commits while the paired update lags or rounds away.
- Invariant to test: `Accounts`, `index ownership`, and user-visible balances must conserve value across success, failure, and repetition.
- Expected Immunefi impact: Theft of user funds / unbacked mint or pool insolvency
- Fast validation: Boundary-test zero, minimum, maximum, and just-above-threshold values and assert end-state conservation.
