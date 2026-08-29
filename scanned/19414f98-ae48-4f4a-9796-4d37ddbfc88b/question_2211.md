# Q2211: next-liquidity-index via collateral-remove-redeem: destroy value through a truncation the opposite operation 

## Question
`next-liquidity-index` (mainnet/contracts/vault/v0-vault-stx.clar:392) rounds the liquidity multiplier down while `next-index` rounds the debt multiplier up over the same interval. Can an unprivileged caller of `collateral-remove-redeem` (mainnet/contracts/market/v0-4-market.clar:1211), by choosing `receiver` for the underlying leg, use that to destroy value through a truncation the opposite operation does not restore, violating the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt` and producing permanent freezing of a position that can never be closed?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:392` -> `next-liquidity-index`
- Entrypoint: `collateral-remove-redeem` (`mainnet/contracts/market/v0-4-market.clar:1211`), unprivileged and publicly callable
- Attacker controls: `receiver` for the underlying leg
- Exploit idea: `next-liquidity-index` rounds the liquidity multiplier down while `next-index` rounds the debt multiplier up over the same interval. Reach it through `collateral-remove-redeem` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Snapshot every state variable `next-liquidity-index` touches, run `collateral-remove-redeem` with `receiver` for the underlying leg, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
