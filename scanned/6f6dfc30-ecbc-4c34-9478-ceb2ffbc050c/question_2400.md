# Q2400: calc-utilization via repay: credit one side of an accounting pair without the other

## Question
Does `repay` (mainnet/contracts/market/v0-4-market.clar:1316) let an unprivileged attacker who controls `on-behalf-of`, naming any third-party principal reach `calc-utilization` (mainnet/contracts/vault/v0-vault-stx.clar:164) in a state where it credit one side of an accounting pair without the other? Given that it divides debt by available liquidity, which can exceed BPS when debt outruns assets, the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal breaks and the result is permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:164` -> `calc-utilization`
- Entrypoint: `repay` (`mainnet/contracts/market/v0-4-market.clar:1316`), unprivileged and publicly callable
- Attacker controls: `on-behalf-of`, naming any third-party principal
- Exploit idea: `calc-utilization` divides debt by available liquidity, which can exceed BPS when debt outruns assets. Reach it through `repay` and credit one side of an accounting pair without the other.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz `on-behalf-of`, naming any third-party principal across its boundary values through `repay` in simnet and assert `calc-utilization` never returns a value that breaks the invariant.
