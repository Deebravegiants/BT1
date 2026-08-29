# Q4890: total-debt via supply-collateral-add: destroy value through a truncation the opposite operation 

## Question
Entering through `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175) while controlling vault share price at the moment of the deposit leg, can an unprivileged attacker make `total-debt` (mainnet/contracts/vault/v0-vault-stx.clar:328) destroy value through a truncation the opposite operation does not restore? `total-debt` computes cumulative debt from `principal-scaled` and `index`, so the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal would fail, yielding permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:328` -> `total-debt`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: vault share price at the moment of the deposit leg
- Exploit idea: `total-debt` computes cumulative debt from `principal-scaled` and `index`. Reach it through `supply-collateral-add` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz vault share price at the moment of the deposit leg across its boundary values through `supply-collateral-add` in simnet and assert `total-debt` never returns a value that breaks the invariant.
