# Q3526: updateRSETHPrice Fee On Transfer Token Skew Rounding LRTOracle P3526

## Question
Can an unprivileged public caller enter through `public updateRSETHPrice()` while controlling call timing after deposits, withdrawals, reward sends, donations, or external balance changes and use a supported ERC20 path where received balance is lower than depositAmount or transfer amount, causing `contracts/LRTOracle.sol::updateRSETHPrice` to break the invariant that minted rsETH and committed withdrawals are based on actual assets received; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice, leading to direct theft of user funds? Probe condition: LRTOracle price route; amount case available liquidity exactly; timing immediately after reward sendFunds; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::updateRSETHPrice
- Entrypoint: public updateRSETHPrice()
- Attacker controls: call timing after deposits, withdrawals, reward sends, donations, or external balance changes; scenario: use a supported ERC20 path where received balance is lower than depositAmount or transfer amount; validation style: stateful fuzzing over deposit, update price, withdraw, unlock, complete; probe condition: LRTOracle price route; amount case available liquidity exactly; timing immediately after reward sendFunds; caller model EOA caller
- Exploit idea: Use stateful invariant fuzz to exercise the fee-on-transfer token skew path against updateRSETHPrice and look for rounding breaking value conservation or liveness.
- Invariant to test: minted rsETH and committed withdrawals are based on actual assets received; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice
- Expected Immunefi impact: Critical. Direct theft of any user funds, whether at-rest or in-motion, other than unclaimed yield
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: LRTOracle price route; amount case available liquidity exactly; timing immediately after reward sendFunds; caller model EOA caller.
