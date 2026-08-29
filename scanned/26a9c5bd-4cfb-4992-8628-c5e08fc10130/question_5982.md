# Q5982: vault-accrue via supply-collateral-add: credit one side of an accounting pair without the other

## Question
Entering through `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175) while controlling the `ft` trait principal deciding which vault is routed to, can an unprivileged attacker make `vault-accrue` (mainnet/contracts/market/v0-4-market.clar:189) credit one side of an accounting pair without the other? `vault-accrue` dispatches accrual to one of six vaults by asset id, so the invariant that every round-up has a paired round-down that repetition cannot exploit would fail, yielding permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:189` -> `vault-accrue`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal deciding which vault is routed to
- Exploit idea: `vault-accrue` dispatches accrual to one of six vaults by asset id. Reach it through `supply-collateral-add` and credit one side of an accounting pair without the other.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz the `ft` trait principal deciding which vault is routed to across its boundary values through `supply-collateral-add` in simnet and assert `vault-accrue` never returns a value that breaks the invariant.
