# Q2495: accrue-collateral-asset via liquidate-redeem: destroy value through a truncation the opposite operation 

## Question
`accrue-collateral-asset` (mainnet/contracts/market/v0-4-market.clar:273) maps a ztoken id to a vault id through a chain of `is-eq` tests that falls through to the u100 sentinel. Can an unprivileged caller of `liquidate-redeem` (mainnet/contracts/market/v0-4-market.clar:1604), by choosing the seized zToken amount that is immediately redeemed, use that to destroy value through a truncation the opposite operation does not restore, violating the invariant that value leaving a call equals value entering plus value minted minus value burned and producing protocol insolvency?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:273` -> `accrue-collateral-asset`
- Entrypoint: `liquidate-redeem` (`mainnet/contracts/market/v0-4-market.clar:1604`), unprivileged and publicly callable
- Attacker controls: the seized zToken amount that is immediately redeemed
- Exploit idea: `accrue-collateral-asset` maps a ztoken id to a vault id through a chain of `is-eq` tests that falls through to the u100 sentinel. Reach it through `liquidate-redeem` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Run the baseline `liquidate-redeem` call, then the attacker-shaped one with the seized zToken amount that is immediately redeemed, and assert the attacker's net token balance change is zero or negative.
