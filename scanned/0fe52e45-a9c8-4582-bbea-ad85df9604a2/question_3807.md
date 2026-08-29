# Q3807: scale-debt-for-liquidation via liquidate-redeem: count one deposit as backing for two simultaneous claims

## Question
`scale-debt-for-liquidation` (mainnet/contracts/market/v0-4-market.clar:858) re-scales collateral by `scaled-to-remove / scaled-debt` after the debt was already capped. Can an unprivileged caller of `liquidate-redeem` (mainnet/contracts/market/v0-4-market.clar:1604), by choosing the redemption receiver, use that to count one deposit as backing for two simultaneous claims, violating the invariant that every round-up has a paired round-down that repetition cannot exploit and producing permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:858` -> `scale-debt-for-liquidation`
- Entrypoint: `liquidate-redeem` (`mainnet/contracts/market/v0-4-market.clar:1604`), unprivileged and publicly callable
- Attacker controls: the redemption receiver
- Exploit idea: `scale-debt-for-liquidation` re-scales collateral by `scaled-to-remove / scaled-debt` after the debt was already capped. Reach it through `liquidate-redeem` and count one deposit as backing for two simultaneous claims.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `scale-debt-for-liquidation` touches, run `liquidate-redeem` with the redemption receiver, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
