# Q3592: updateRSETHPrice FirstExcludedIndex Boundary Rounding Aave P3592

## Question
Can an unprivileged public caller enter through `public updateRSETHPrice()` while controlling call timing after deposits, withdrawals, reward sends, donations, or external balance changes and fill withdrawal requests around the unlockQueue firstExcludedIndex boundary, causing `contracts/LRTOracle.sol::updateRSETHPrice` to break the invariant that unlocking cannot skip, over-unlock, or permanently strand requests; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice, leading to direct theft of user funds? Probe condition: Aave aWETH liquidity route; amount case deposit limit plus 1 wei; timing immediately after reward sendFunds; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::updateRSETHPrice
- Entrypoint: public updateRSETHPrice()
- Attacker controls: call timing after deposits, withdrawals, reward sends, donations, or external balance changes; scenario: fill withdrawal requests around the unlockQueue firstExcludedIndex boundary; validation style: a fork test using current deployed balances and supported assets; probe condition: Aave aWETH liquidity route; amount case deposit limit plus 1 wei; timing immediately after reward sendFunds; caller model EOA caller
- Exploit idea: Use forked-mainnet state to exercise the firstExcludedIndex boundary path against updateRSETHPrice and look for rounding breaking value conservation or liveness.
- Invariant to test: unlocking cannot skip, over-unlock, or permanently strand requests; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice
- Expected Immunefi impact: Critical. Direct theft of any user funds, whether at-rest or in-motion, other than unclaimed yield
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: Aave aWETH liquidity route; amount case deposit limit plus 1 wei; timing immediately after reward sendFunds; caller model EOA caller.
