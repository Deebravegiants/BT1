# Q5046: vault-socialize-debt via liquidate-redeem: count one deposit as backing for two simultaneous claims

## Question
Entering through `liquidate-redeem` (mainnet/contracts/market/v0-4-market.clar:1604) while controlling the vault whose share price the redemption moves, can an unprivileged attacker make `vault-socialize-debt` (mainnet/contracts/market/v0-4-market.clar:216) count one deposit as backing for two simultaneous claims? `vault-socialize-debt` routes a scaled write-down to one of six vaults, so the invariant that value leaving a call equals value entering plus value minted minus value burned would fail, yielding permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:216` -> `vault-socialize-debt`
- Entrypoint: `liquidate-redeem` (`mainnet/contracts/market/v0-4-market.clar:1604`), unprivileged and publicly callable
- Attacker controls: the vault whose share price the redemption moves
- Exploit idea: `vault-socialize-debt` routes a scaled write-down to one of six vaults. Reach it through `liquidate-redeem` and count one deposit as backing for two simultaneous claims.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz the vault whose share price the redemption moves across its boundary values through `liquidate-redeem` in simnet and assert `vault-socialize-debt` never returns a value that breaks the invariant.
