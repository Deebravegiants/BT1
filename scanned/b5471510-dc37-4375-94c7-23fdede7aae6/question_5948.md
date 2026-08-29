# Q5948: resolve-callcode via supply-collateral-add: have the same quantity scaled twice by two contracts that 

## Question
Does `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175) let an unprivileged attacker who controls vault share price at the moment of the deposit leg reach `resolve-callcode` (mainnet/contracts/market/v0-4-market.clar:349) in a state where it have the same quantity scaled twice by two contracts that round differently? Given that it chains callcode transforms, with CALLCODE-ZSTSTX composing `resolve-ztoken` over `resolve-ststx`, the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal breaks and the result is permanent freezing of unclaimed yield.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:349` -> `resolve-callcode`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: vault share price at the moment of the deposit leg
- Exploit idea: `resolve-callcode` chains callcode transforms, with CALLCODE-ZSTSTX composing `resolve-ztoken` over `resolve-ststx`. Reach it through `supply-collateral-add` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: High - permanent freezing of unclaimed yield
- Fast validation: Write a Clarinet simnet test calling `supply-collateral-add` twice with vault share price at the moment of the deposit leg varied, and assert that the value `resolve-callcode` returns is identical in both runs; a divergence confirms the finding.
