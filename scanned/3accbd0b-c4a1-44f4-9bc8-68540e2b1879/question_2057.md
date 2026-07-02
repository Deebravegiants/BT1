# Q2057: getRsETHAmountToMint FirstExcludedIndex Boundary Stale Price daily P2057

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)` while controlling asset, amount, minRSETHAmountExpected and transaction ordering and fill withdrawal requests around the unlockQueue firstExcludedIndex boundary, causing `contracts/LRTDepositPool.sol::getRsETHAmountToMint` to break the invariant that unlocking cannot skip, over-unlock, or permanently strand requests; specifically, stale price must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint, leading to direct theft of user funds? Probe condition: daily mint limit route; amount case minAmount minus 1 wei; timing one second before daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getRsETHAmountToMint
- Entrypoint: depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)
- Attacker controls: asset, amount, minRSETHAmountExpected and transaction ordering; scenario: fill withdrawal requests around the unlockQueue firstExcludedIndex boundary; validation style: several attacker accounts creating adjacent requests; probe condition: daily mint limit route; amount case minAmount minus 1 wei; timing one second before daily reset; caller model EOA caller
- Exploit idea: Use multi-account queue pressure to exercise the firstExcludedIndex boundary path against getRsETHAmountToMint and look for stale price breaking value conservation or liveness.
- Invariant to test: unlocking cannot skip, over-unlock, or permanently strand requests; specifically, stale price must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint
- Expected Immunefi impact: Critical. Direct theft of any user funds, whether at-rest or in-motion, other than unclaimed yield
- Fast validation: sequence price update/deposit/withdraw with stale and fresh prices and assert no profitable round trip. Use probe condition: daily mint limit route; amount case minAmount minus 1 wei; timing one second before daily reset; caller model EOA caller.
