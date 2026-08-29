# Q2153: calc-index-next via liquidate-multi: mint shares whose backing was never received

## Question
Can an unprivileged attacker entering through `liquidate-multi` (mainnet/contracts/market/v0-4-market.clar:1593), controlling which borrowers are placed early versus late in the batch, drive `calc-index-next` (mainnet/contracts/vault/v0-vault-stx.clar:183) — which applies a multiplier to the current index — to mint shares whose backing was never received, breaking the invariant that shares outstanding valued at the current share price never exceed `total-assets`, and cause protocol insolvency?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:183` -> `calc-index-next`
- Entrypoint: `liquidate-multi` (`mainnet/contracts/market/v0-4-market.clar:1593`), unprivileged and publicly callable
- Attacker controls: which borrowers are placed early versus late in the batch
- Exploit idea: `calc-index-next` applies a multiplier to the current index. Reach it through `liquidate-multi` and mint shares whose backing was never received.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Run the baseline `liquidate-multi` call, then the attacker-shaped one with which borrowers are placed early versus late in the batch, and assert the attacker's net token balance change is zero or negative.
