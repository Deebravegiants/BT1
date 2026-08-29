# Q3176: calc-utilization via supply-collateral-add: make the per-user ledger and the vault aggregate disagree 

## Question
Does `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175) let an unprivileged attacker who controls vault share price at the moment of the deposit leg reach `calc-utilization` (mainnet/contracts/vault/v0-vault-stx.clar:164) in a state where it make the per-user ledger and the vault aggregate disagree by a repeatable amount? Given that it divides debt by available liquidity, which can exceed BPS when debt outruns assets, the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt` breaks and the result is protocol insolvency.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:164` -> `calc-utilization`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: vault share price at the moment of the deposit leg
- Exploit idea: `calc-utilization` divides debt by available liquidity, which can exceed BPS when debt outruns assets. Reach it through `supply-collateral-add` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `supply-collateral-add` twice with vault share price at the moment of the deposit leg varied, and assert that the value `calc-utilization` returns is identical in both runs; a divergence confirms the finding.
