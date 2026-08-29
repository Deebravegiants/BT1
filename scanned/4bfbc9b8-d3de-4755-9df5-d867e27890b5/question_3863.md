# Q3863: find-collateral-amount via liquidate: count one deposit as backing for two simultaneous claims

## Question
`find-collateral-amount` (mainnet/contracts/market/v0-4-market.clar:609) returns u0 for an absent asset, making a missing row indistinguishable from a zero holding. Can an unprivileged caller of `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382), by choosing `debt-amount`, use that to count one deposit as backing for two simultaneous claims, violating the invariant that every round-up has a paired round-down that repetition cannot exploit and producing protocol insolvency?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:609` -> `find-collateral-amount`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `debt-amount`
- Exploit idea: `find-collateral-amount` returns u0 for an absent asset, making a missing row indistinguishable from a zero holding. Reach it through `liquidate` and count one deposit as backing for two simultaneous claims.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Run the baseline `liquidate` call, then the attacker-shaped one with `debt-amount`, and assert the attacker's net token balance change is zero or negative.
