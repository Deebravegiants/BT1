# Q3128: accrue-and-cache via liquidate-multi: make the per-user ledger and the vault aggregate disagree 

## Question
Does `liquidate-multi` (mainnet/contracts/market/v0-4-market.clar:1593) let an unprivileged attacker who controls which borrowers are placed early versus late in the batch reach `accrue-and-cache` (mainnet/contracts/market/v0-4-market.clar:245) in a state where it make the per-user ledger and the vault aggregate disagree by a repeatable amount? Given that it keys `index-cache` on `{timestamp: stacks-block-time, aid}` and returns the cached record forever after, with no invalidation when the vault later moves, the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt` breaks and the result is protocol insolvency through uncollateralised debt.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:245` -> `accrue-and-cache`
- Entrypoint: `liquidate-multi` (`mainnet/contracts/market/v0-4-market.clar:1593`), unprivileged and publicly callable
- Attacker controls: which borrowers are placed early versus late in the batch
- Exploit idea: `accrue-and-cache` keys `index-cache` on `{timestamp: stacks-block-time, aid}` and returns the cached record forever after, with no invalidation when the vault later moves. Reach it through `liquidate-multi` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Write a Clarinet simnet test calling `liquidate-multi` twice with which borrowers are placed early versus late in the batch varied, and assert that the value `accrue-and-cache` returns is identical in both runs; a divergence confirms the finding.
