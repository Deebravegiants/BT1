# Q2832: calc-utilization via redeem: credit one side of an accounting pair without the other

## Question
Does `redeem` (mainnet/contracts/vault/v0-vault-stx.clar:797) let an unprivileged attacker who controls the vault's available liquidity relative to the redemption reach `calc-utilization` (mainnet/contracts/vault/v0-vault-stx.clar:164) in a state where it credit one side of an accounting pair without the other? Given that it divides debt by available liquidity, which can exceed BPS when debt outruns assets, the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal breaks and the result is permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:164` -> `calc-utilization`
- Entrypoint: `redeem` (`mainnet/contracts/vault/v0-vault-stx.clar:797`), unprivileged and publicly callable
- Attacker controls: the vault's available liquidity relative to the redemption
- Exploit idea: `calc-utilization` divides debt by available liquidity, which can exceed BPS when debt outruns assets. Reach it through `redeem` and credit one side of an accounting pair without the other.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz the vault's available liquidity relative to the redemption across its boundary values through `redeem` in simnet and assert `calc-utilization` never returns a value that breaks the invariant.
