# Q1506: debt-remove-scaled via liquidate-redeem: record a repayment larger than the value actually delivere

## Question
Entering through `liquidate-redeem` (mainnet/contracts/market/v0-4-market.clar:1604) while controlling the vault whose share price the redemption moves, can an unprivileged attacker make `debt-remove-scaled` (mainnet/contracts/market/v0-market-vault.clar:473) record a repayment larger than the value actually delivered? `debt-remove-scaled` clears the debt bit only when the remaining scaled debt is exactly zero, so the invariant that value leaving a call equals value entering plus value minted minus value burned would fail, yielding permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:473` -> `debt-remove-scaled`
- Entrypoint: `liquidate-redeem` (`mainnet/contracts/market/v0-4-market.clar:1604`), unprivileged and publicly callable
- Attacker controls: the vault whose share price the redemption moves
- Exploit idea: `debt-remove-scaled` clears the debt bit only when the remaining scaled debt is exactly zero. Reach it through `liquidate-redeem` and record a repayment larger than the value actually delivered.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz the vault whose share price the redemption moves across its boundary values through `liquidate-redeem` in simnet and assert `debt-remove-scaled` never returns a value that breaks the invariant.
