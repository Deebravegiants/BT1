# Q5546: resolve-pyth via liquidate-multi: count one deposit as backing for two simultaneous claims

## Question
Entering through `liquidate-multi` (mainnet/contracts/market/v0-4-market.clar:1593) while controlling which borrowers are placed early versus late in the batch, can an unprivileged attacker make `resolve-pyth` (mainnet/contracts/market/v0-4-market.clar:312) count one deposit as backing for two simultaneous claims? `resolve-pyth` reads the Pyth storage record for a 32-byte ident, so the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt` would fail, yielding protocol insolvency.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:312` -> `resolve-pyth`
- Entrypoint: `liquidate-multi` (`mainnet/contracts/market/v0-4-market.clar:1593`), unprivileged and publicly callable
- Attacker controls: which borrowers are placed early versus late in the batch
- Exploit idea: `resolve-pyth` reads the Pyth storage record for a 32-byte ident. Reach it through `liquidate-multi` and count one deposit as backing for two simultaneous claims.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `liquidate-multi` twice with which borrowers are placed early versus late in the batch varied, and assert that the value `resolve-pyth` returns is identical in both runs; a divergence confirms the finding.
