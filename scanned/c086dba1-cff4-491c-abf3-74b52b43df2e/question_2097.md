# Q2097: getRsETHAmountToMint Fee Mint Limit Boundary Oracle daily P2097

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)` while controlling asset, amount, minRSETHAmountExpected and transaction ordering and execute price updates at exactly fee-period or mint-period boundaries, causing `contracts/LRTDepositPool.sol::getRsETHAmountToMint` to break the invariant that daily limits cannot be bypassed or permanently block legitimate minting; specifically, oracle must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint, leading to protocol insolvency? Probe condition: daily mint limit route; amount case minAmount plus 1 wei; timing one second before daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getRsETHAmountToMint
- Entrypoint: depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)
- Attacker controls: asset, amount, minRSETHAmountExpected and transaction ordering; scenario: execute price updates at exactly fee-period or mint-period boundaries; validation style: warp/block-roll around day or withdrawal-delay boundaries; probe condition: daily mint limit route; amount case minAmount plus 1 wei; timing one second before daily reset; caller model EOA caller
- Exploit idea: Use period boundary fuzz to exercise the fee mint limit boundary path against getRsETHAmountToMint and look for oracle breaking value conservation or liveness.
- Invariant to test: daily limits cannot be bypassed or permanently block legitimate minting; specifically, oracle must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: mock the configured price fetcher within sane bounds and assert conversions conserve normalized value Use probe condition: daily mint limit route; amount case minAmount plus 1 wei; timing one second before daily reset; caller model EOA caller.
