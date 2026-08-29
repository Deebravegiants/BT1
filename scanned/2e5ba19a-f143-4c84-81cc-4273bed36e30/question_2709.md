# Q2709: next-liquidity-index via liquidate-multi: mint shares whose backing was never received

## Question
Can an unprivileged attacker entering through `liquidate-multi` (mainnet/contracts/market/v0-4-market.clar:1593), controlling which borrowers are placed early versus late in the batch, drive `next-liquidity-index` (mainnet/contracts/vault/v0-vault-stx.clar:392) — which rounds the liquidity multiplier down while `next-index` rounds the debt multiplier up over the same interval — to mint shares whose backing was never received, breaking the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury, and cause temporary freezing of funds?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:392` -> `next-liquidity-index`
- Entrypoint: `liquidate-multi` (`mainnet/contracts/market/v0-4-market.clar:1593`), unprivileged and publicly callable
- Attacker controls: which borrowers are placed early versus late in the batch
- Exploit idea: `next-liquidity-index` rounds the liquidity multiplier down while `next-index` rounds the debt multiplier up over the same interval. Reach it through `liquidate-multi` and mint shares whose backing was never received.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Snapshot every state variable `next-liquidity-index` touches, run `liquidate-multi` with which borrowers are placed early versus late in the batch, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
