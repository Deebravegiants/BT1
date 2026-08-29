# Q0368: resolve-ststx via borrow: destroy value through a truncation the opposite operation 

## Question
Does `borrow` (mainnet/contracts/market/v0-4-market.clar:1238) let an unprivileged attacker who controls `receiver`, including a contract principal reach `resolve-ststx` (mainnet/contracts/market/v0-4-market.clar:339) in a state where it destroy value through a truncation the opposite operation does not restore? Given that it calls the external stSTX ratio contract inside price resolution and scales by STSTX-RATIO-DECIMALS with `mul-div-down`, the invariant that every round-up has a paired round-down that repetition cannot exploit breaks and the result is permanent freezing of unclaimed yield.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:339` -> `resolve-ststx`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: `receiver`, including a contract principal
- Exploit idea: `resolve-ststx` calls the external stSTX ratio contract inside price resolution and scales by STSTX-RATIO-DECIMALS with `mul-div-down`. Reach it through `borrow` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: High - permanent freezing of unclaimed yield
- Fast validation: Write a Clarinet simnet test calling `borrow` twice with `receiver`, including a contract principal varied, and assert that the value `resolve-ststx` returns is identical in both runs; a divergence confirms the finding.
