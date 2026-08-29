# Q0677: calc-utilization via collateral-add: credit one side of an accounting pair without the other

## Question
Can an unprivileged attacker entering through `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020), controlling whether this asset is already collateral (the is-new-collateral branch), drive `calc-utilization` (mainnet/contracts/vault/v0-vault-stx.clar:164) — which divides debt by available liquidity, which can exceed BPS when debt outruns assets — to credit one side of an accounting pair without the other, breaking the invariant that value leaving a call equals value entering plus value minted minus value burned, and cause protocol insolvency?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:164` -> `calc-utilization`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: whether this asset is already collateral (the is-new-collateral branch)
- Exploit idea: `calc-utilization` divides debt by available liquidity, which can exceed BPS when debt outruns assets. Reach it through `collateral-add` and credit one side of an accounting pair without the other.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Run the baseline `collateral-add` call, then the attacker-shaped one with whether this asset is already collateral (the is-new-collateral branch), and assert the attacker's net token balance change is zero or negative.
