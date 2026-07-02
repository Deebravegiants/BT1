# Q3646: updateRSETHPrice Aave Liquidity Shortfall Rounding LRTOracle P3646

## Question
Can an unprivileged public caller enter through `public updateRSETHPrice()` while controlling call timing after deposits, withdrawals, reward sends, donations, or external balance changes and complete or instant-withdraw ETH when Aave liquidity is lower than accounted aWETH principal, causing `contracts/LRTOracle.sol::updateRSETHPrice` to break the invariant that external liquidity shortfall cannot burn rsETH without paying or freeze completed requests unexpectedly; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice, leading to theft of unclaimed yield? Probe condition: LRTOracle price route; amount case minAmount minus 1 wei; timing immediately after direct ETH donation; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::updateRSETHPrice
- Entrypoint: public updateRSETHPrice()
- Attacker controls: call timing after deposits, withdrawals, reward sends, donations, or external balance changes; scenario: complete or instant-withdraw ETH when Aave liquidity is lower than accounted aWETH principal; validation style: stateful fuzzing over deposit, update price, withdraw, unlock, complete; probe condition: LRTOracle price route; amount case minAmount minus 1 wei; timing immediately after direct ETH donation; caller model EOA caller
- Exploit idea: Use stateful invariant fuzz to exercise the Aave liquidity shortfall path against updateRSETHPrice and look for rounding breaking value conservation or liveness.
- Invariant to test: external liquidity shortfall cannot burn rsETH without paying or freeze completed requests unexpectedly; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice
- Expected Immunefi impact: High. Theft of unclaimed yield
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: LRTOracle price route; amount case minAmount minus 1 wei; timing immediately after direct ETH donation; caller model EOA caller.
