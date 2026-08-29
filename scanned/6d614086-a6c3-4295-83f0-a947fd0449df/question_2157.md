# Q2157: system-repay via liquidate-multi: mint shares whose backing was never received

## Question
Can an unprivileged attacker entering through `liquidate-multi` (mainnet/contracts/market/v0-4-market.clar:1593), controlling which borrowers are placed early versus late in the batch, drive `system-repay` (mainnet/contracts/vault/v0-vault-stx.clar:902) — which splits one payment with three different formulas for `principal-reduction`, `principal-repaid` and `interest-paid` — to mint shares whose backing was never received, breaking the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury, and cause permanent freezing of a position that can never be closed?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:902` -> `system-repay`
- Entrypoint: `liquidate-multi` (`mainnet/contracts/market/v0-4-market.clar:1593`), unprivileged and publicly callable
- Attacker controls: which borrowers are placed early versus late in the batch
- Exploit idea: `system-repay` splits one payment with three different formulas for `principal-reduction`, `principal-repaid` and `interest-paid`. Reach it through `liquidate-multi` and mint shares whose backing was never received.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Snapshot every state variable `system-repay` touches, run `liquidate-multi` with which borrowers are placed early versus late in the batch, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
