# Q2059: getRsETHAmountToMint FirstExcludedIndex Boundary Rounding Lido P2059

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)` while controlling asset, amount, minRSETHAmountExpected and transaction ordering and fill withdrawal requests around the unlockQueue firstExcludedIndex boundary, causing `contracts/LRTDepositPool.sol::getRsETHAmountToMint` to break the invariant that unlocking cannot skip, over-unlock, or permanently strand requests; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint, leading to failure to deliver promised returns without principal loss? Probe condition: Lido stETH unstake route; amount case minAmount minus 1 wei; timing one second before daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getRsETHAmountToMint
- Entrypoint: depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)
- Attacker controls: asset, amount, minRSETHAmountExpected and transaction ordering; scenario: fill withdrawal requests around the unlockQueue firstExcludedIndex boundary; validation style: an attacker contract as msg.sender or recipient; probe condition: Lido stETH unstake route; amount case minAmount minus 1 wei; timing one second before daily reset; caller model EOA caller
- Exploit idea: Use receiver contract path to exercise the firstExcludedIndex boundary path against getRsETHAmountToMint and look for rounding breaking value conservation or liveness.
- Invariant to test: unlocking cannot skip, over-unlock, or permanently strand requests; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: Lido stETH unstake route; amount case minAmount minus 1 wei; timing one second before daily reset; caller model EOA caller.
