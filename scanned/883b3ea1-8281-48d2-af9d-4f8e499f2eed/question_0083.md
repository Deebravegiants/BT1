# Q0083: interlace can break Regions / Workplan conservation

## Question
Can an unprivileged attacker call `interlace` with crafted amounts, fees, or prices, IDs, hashes, nonces, or location fields so `Regions` and `Workplan` diverge for the same economic action, enabling theft, unbacked minting, or hidden debt?

## Target
- File/function: substrate/frame/broker/src/lib.rs::interlace
- Entrypoint: signed extrinsic `interlace`
- Attacker controls: amounts, fees, or prices, IDs, hashes, nonces, or location fields
- Exploit idea: Stress exact-threshold accounting so one side of the debit/credit path commits while the paired update lags or rounds away.
- Invariant to test: `Regions`, `Workplan`, and user-visible balances must conserve value across success, failure, and repetition.
- Expected Immunefi impact: Theft of user funds / unbacked mint or pool insolvency
- Fast validation: Boundary-test zero, minimum, maximum, and just-above-threshold values and assert end-state conservation.
