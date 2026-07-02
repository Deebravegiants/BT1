# Q2094: getRsETHAmountToMint Fee Mint Limit Boundary Stale Price deposit-limit P2094

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)` while controlling asset, amount, minRSETHAmountExpected and transaction ordering and execute price updates at exactly fee-period or mint-period boundaries, causing `contracts/LRTDepositPool.sol::getRsETHAmountToMint` to break the invariant that daily limits cannot be bypassed or permanently block legitimate minting; specifically, stale price must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint, leading to protocol insolvency? Probe condition: deposit-limit accounting route; amount case minAmount plus 1 wei; timing one second before daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getRsETHAmountToMint
- Entrypoint: depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)
- Attacker controls: asset, amount, minRSETHAmountExpected and transaction ordering; scenario: execute price updates at exactly fee-period or mint-period boundaries; validation style: compare many dust calls against one large call; probe condition: deposit-limit accounting route; amount case minAmount plus 1 wei; timing one second before daily reset; caller model EOA caller
- Exploit idea: Use dust-to-large differential to exercise the fee mint limit boundary path against getRsETHAmountToMint and look for stale price breaking value conservation or liveness.
- Invariant to test: daily limits cannot be bypassed or permanently block legitimate minting; specifically, stale price must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: sequence price update/deposit/withdraw with stale and fresh prices and assert no profitable round trip. Use probe condition: deposit-limit accounting route; amount case minAmount plus 1 wei; timing one second before daily reset; caller model EOA caller.
