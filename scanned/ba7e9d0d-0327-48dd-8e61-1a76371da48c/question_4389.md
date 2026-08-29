# Q4389: principal-ratio-reduction via collateral-remove-redeem: have the same quantity scaled twice by two contracts that 

## Question
Can an unprivileged attacker entering through `collateral-remove-redeem` (mainnet/contracts/market/v0-4-market.clar:1211), controlling `receiver` for the underlying leg, drive `principal-ratio-reduction` (mainnet/contracts/vault/v0-vault-stx.clar:406) — which derives a principal reduction from an amount, the scaled principal and the previewed debt — to have the same quantity scaled twice by two contracts that round differently, breaking the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`, and cause permanent freezing of a position that can never be closed?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:406` -> `principal-ratio-reduction`
- Entrypoint: `collateral-remove-redeem` (`mainnet/contracts/market/v0-4-market.clar:1211`), unprivileged and publicly callable
- Attacker controls: `receiver` for the underlying leg
- Exploit idea: `principal-ratio-reduction` derives a principal reduction from an amount, the scaled principal and the previewed debt. Reach it through `collateral-remove-redeem` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Snapshot every state variable `principal-ratio-reduction` touches, run `collateral-remove-redeem` with `receiver` for the underlying leg, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
