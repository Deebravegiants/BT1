# Q2293: getRsETHAmountToMint Block Timestamp Boundary Stale Price Merkle-free P2293

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)` while controlling asset, amount, minRSETHAmountExpected and transaction ordering and execute calls exactly at delay, daily reset, or period boundary blocks, causing `contracts/LRTDepositPool.sol::getRsETHAmountToMint` to break the invariant that boundary equality cannot bypass delay, limits, or settlement ordering; specifically, stale price must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint, leading to protocol insolvency? Probe condition: Merkle-free yield accounting route; amount case daily limit exactly; timing one second before daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getRsETHAmountToMint
- Entrypoint: depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)
- Attacker controls: asset, amount, minRSETHAmountExpected and transaction ordering; scenario: execute calls exactly at delay, daily reset, or period boundary blocks; validation style: one transaction using a contract wallet and controlled calldata; probe condition: Merkle-free yield accounting route; amount case daily limit exactly; timing one second before daily reset; caller model EOA caller
- Exploit idea: Use single transaction to exercise the block-timestamp boundary path against getRsETHAmountToMint and look for stale price breaking value conservation or liveness.
- Invariant to test: boundary equality cannot bypass delay, limits, or settlement ordering; specifically, stale price must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: sequence price update/deposit/withdraw with stale and fresh prices and assert no profitable round trip. Use probe condition: Merkle-free yield accounting route; amount case daily limit exactly; timing one second before daily reset; caller model EOA caller.
