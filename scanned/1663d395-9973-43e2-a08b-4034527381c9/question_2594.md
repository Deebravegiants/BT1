# Q2594: convert-to-assets-preview via liquidate-redeem: have the same quantity scaled twice by two contracts that 

## Question
Entering through `liquidate-redeem` (mainnet/contracts/market/v0-4-market.clar:1604) while controlling the borrower targeted, can an unprivileged attacker make `convert-to-assets-preview` (mainnet/contracts/vault/v0-vault-stx.clar:317) have the same quantity scaled twice by two contracts that round differently? `convert-to-assets-preview` prices a redemption against `total-assets-preview` and `total-supply-preview`, so the invariant that every round-up has a paired round-down that repetition cannot exploit would fail, yielding protocol insolvency.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:317` -> `convert-to-assets-preview`
- Entrypoint: `liquidate-redeem` (`mainnet/contracts/market/v0-4-market.clar:1604`), unprivileged and publicly callable
- Attacker controls: the borrower targeted
- Exploit idea: `convert-to-assets-preview` prices a redemption against `total-assets-preview` and `total-supply-preview`. Reach it through `liquidate-redeem` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `liquidate-redeem` twice with the borrower targeted varied, and assert that the value `convert-to-assets-preview` returns is identical in both runs; a divergence confirms the finding.
