# Q2672: resolve-pyth via collateral-remove: credit one side of an accounting pair without the other

## Question
Does `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107) let an unprivileged attacker who controls whether the position has any enabled debt row (the has-debt branch) reach `resolve-pyth` (mainnet/contracts/market/v0-4-market.clar:312) in a state where it credit one side of an accounting pair without the other? Given that it reads the Pyth storage record for a 32-byte ident, the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal breaks and the result is protocol insolvency.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:312` -> `resolve-pyth`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: whether the position has any enabled debt row (the has-debt branch)
- Exploit idea: `resolve-pyth` reads the Pyth storage record for a 32-byte ident. Reach it through `collateral-remove` and credit one side of an accounting pair without the other.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `collateral-remove` twice with whether the position has any enabled debt row (the has-debt branch) varied, and assert that the value `resolve-pyth` returns is identical in both runs; a divergence confirms the finding.
