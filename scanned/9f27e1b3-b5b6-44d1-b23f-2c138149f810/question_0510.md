# Q0510: calc-liquidation-params via liquidate-redeem: mint shares whose backing was never received

## Question
Entering through `liquidate-redeem` (mainnet/contracts/market/v0-4-market.clar:1604) while controlling the redemption receiver, can an unprivileged attacker make `calc-liquidation-params` (mainnet/contracts/market/v0-4-market.clar:739) mint shares whose backing was never received? `calc-liquidation-params` chains the factor, the exponent curve, the penalty bound and the max repayable amount in one helper, so the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal would fail, yielding permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:739` -> `calc-liquidation-params`
- Entrypoint: `liquidate-redeem` (`mainnet/contracts/market/v0-4-market.clar:1604`), unprivileged and publicly callable
- Attacker controls: the redemption receiver
- Exploit idea: `calc-liquidation-params` chains the factor, the exponent curve, the penalty bound and the max repayable amount in one helper. Reach it through `liquidate-redeem` and mint shares whose backing was never received.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz the redemption receiver across its boundary values through `liquidate-redeem` in simnet and assert `calc-liquidation-params` never returns a value that breaks the invariant.
