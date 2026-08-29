# Q1122: increment via liquidate-redeem: record a repayment larger than the value actually delivere

## Question
Entering through `liquidate-redeem` (mainnet/contracts/market/v0-4-market.clar:1604) while controlling the vault whose share price the redemption moves, can an unprivileged attacker make `increment` (mainnet/contracts/market/v0-market-vault.clar:137) record a repayment larger than the value actually delivered? `increment` advances the user-id nonce, so the invariant that value leaving a call equals value entering plus value minted minus value burned would fail, yielding permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:137` -> `increment`
- Entrypoint: `liquidate-redeem` (`mainnet/contracts/market/v0-4-market.clar:1604`), unprivileged and publicly callable
- Attacker controls: the vault whose share price the redemption moves
- Exploit idea: `increment` advances the user-id nonce. Reach it through `liquidate-redeem` and record a repayment larger than the value actually delivered.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz the vault whose share price the redemption moves across its boundary values through `liquidate-redeem` in simnet and assert `increment` never returns a value that breaks the invariant.
