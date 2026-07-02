# Q1964: getRsETHAmountToMint Zero Or Dust Edge Oracle rsETH P1964

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)` while controlling asset, amount, minRSETHAmountExpected and transaction ordering and use zero-like, one-wei, or min-threshold-adjacent amounts to bypass accounting updates, causing `contracts/LRTDepositPool.sol::getRsETHAmountToMint` to break the invariant that dust inputs cannot create withdrawable value or stuck committed assets; specifically, oracle must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint, leading to protocol insolvency? Probe condition: rsETH burn route; amount case deposit limit minus 1 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getRsETHAmountToMint
- Entrypoint: depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)
- Attacker controls: asset, amount, minRSETHAmountExpected and transaction ordering; scenario: use zero-like, one-wei, or min-threshold-adjacent amounts to bypass accounting updates; validation style: compare ETH, stETH, and ETHx branches under the same value; probe condition: rsETH burn route; amount case deposit limit minus 1 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller
- Exploit idea: Use asset pair differential to exercise the zero-or-dust edge path against getRsETHAmountToMint and look for oracle breaking value conservation or liveness.
- Invariant to test: dust inputs cannot create withdrawable value or stuck committed assets; specifically, oracle must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: mock the configured price fetcher within sane bounds and assert conversions conserve normalized value Use probe condition: rsETH burn route; amount case deposit limit minus 1 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.
