# Q2303: getRsETHAmountToMint Block Timestamp Boundary Rounding ETHx P2303

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)` while controlling asset, amount, minRSETHAmountExpected and transaction ordering and execute calls exactly at delay, daily reset, or period boundary blocks, causing `contracts/LRTDepositPool.sol::getRsETHAmountToMint` to break the invariant that boundary equality cannot bypass delay, limits, or settlement ordering; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint, leading to failure to deliver promised returns without principal loss? Probe condition: ETHx supported asset route; amount case available liquidity minus 1 wei; timing one second before daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getRsETHAmountToMint
- Entrypoint: depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)
- Attacker controls: asset, amount, minRSETHAmountExpected and transaction ordering; scenario: execute calls exactly at delay, daily reset, or period boundary blocks; validation style: a local supported-token harness with configurable transfer behavior; probe condition: ETHx supported asset route; amount case available liquidity minus 1 wei; timing one second before daily reset; caller model EOA caller
- Exploit idea: Use malicious ERC20 harness to exercise the block-timestamp boundary path against getRsETHAmountToMint and look for rounding breaking value conservation or liveness.
- Invariant to test: boundary equality cannot bypass delay, limits, or settlement ordering; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: ETHx supported asset route; amount case available liquidity minus 1 wei; timing one second before daily reset; caller model EOA caller.
