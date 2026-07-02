# Q526: depositAsset FirstExcludedIndex Boundary Rounding LRTOracle P0526

## Question
Can an unprivileged LST depositor enter through `external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)` while controlling asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior and fill withdrawal requests around the unlockQueue firstExcludedIndex boundary, causing `contracts/LRTDepositPool.sol::depositAsset` to break the invariant that unlocking cannot skip, over-unlock, or permanently strand requests; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for depositAsset, leading to direct theft of user funds? Probe condition: LRTOracle price route; amount case 0.001 ether; timing same block after updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositAsset
- Entrypoint: external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)
- Attacker controls: asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior; scenario: fill withdrawal requests around the unlockQueue firstExcludedIndex boundary; validation style: stateful fuzzing over deposit, update price, withdraw, unlock, complete; probe condition: LRTOracle price route; amount case 0.001 ether; timing same block after updateRSETHPrice; caller model EOA caller
- Exploit idea: Use stateful invariant fuzz to exercise the firstExcludedIndex boundary path against depositAsset and look for rounding breaking value conservation or liveness.
- Invariant to test: unlocking cannot skip, over-unlock, or permanently strand requests; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for depositAsset
- Expected Immunefi impact: Critical. Direct theft of any user funds, whether at-rest or in-motion, other than unclaimed yield
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: LRTOracle price route; amount case 0.001 ether; timing same block after updateRSETHPrice; caller model EOA caller.
