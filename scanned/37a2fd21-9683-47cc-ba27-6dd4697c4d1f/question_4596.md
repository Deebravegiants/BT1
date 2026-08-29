# Q4596: convert-to-assets-preview via collateral-remove-redeem: mint shares whose backing was never received

## Question
Does `collateral-remove-redeem` (mainnet/contracts/market/v0-4-market.clar:1211) let an unprivileged attacker who controls remaining zToken collateral whose price moves with the redeem reach `convert-to-assets-preview` (mainnet/contracts/vault/v0-vault-stx.clar:317) in a state where it mint shares whose backing was never received? Given that it prices a redemption against `total-assets-preview` and `total-supply-preview`, the invariant that every round-up has a paired round-down that repetition cannot exploit breaks and the result is permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:317` -> `convert-to-assets-preview`
- Entrypoint: `collateral-remove-redeem` (`mainnet/contracts/market/v0-4-market.clar:1211`), unprivileged and publicly callable
- Attacker controls: remaining zToken collateral whose price moves with the redeem
- Exploit idea: `convert-to-assets-preview` prices a redemption against `total-assets-preview` and `total-supply-preview`. Reach it through `collateral-remove-redeem` and mint shares whose backing was never received.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz remaining zToken collateral whose price moves with the redeem across its boundary values through `collateral-remove-redeem` in simnet and assert `convert-to-assets-preview` never returns a value that breaks the invariant.
