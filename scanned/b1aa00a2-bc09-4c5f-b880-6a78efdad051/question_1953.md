# Q1953: getRsETHAmountToMint Round Up Insolvency Oracle Merkle-free P1953

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)` while controlling asset, amount, minRSETHAmountExpected and transaction ordering and choose amounts just above precision boundaries so liabilities round up while assets round down, causing `contracts/LRTDepositPool.sol::getRsETHAmountToMint` to break the invariant that rsETH liabilities never exceed normalized protocol assets; specifically, oracle must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint, leading to protocol insolvency? Probe condition: Merkle-free yield accounting route; amount case available liquidity plus 1 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getRsETHAmountToMint
- Entrypoint: depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)
- Attacker controls: asset, amount, minRSETHAmountExpected and transaction ordering; scenario: choose amounts just above precision boundaries so liabilities round up while assets round down; validation style: warp/block-roll around day or withdrawal-delay boundaries; probe condition: Merkle-free yield accounting route; amount case available liquidity plus 1 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller
- Exploit idea: Use period boundary fuzz to exercise the round-up insolvency path against getRsETHAmountToMint and look for oracle breaking value conservation or liveness.
- Invariant to test: rsETH liabilities never exceed normalized protocol assets; specifically, oracle must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: mock the configured price fetcher within sane bounds and assert conversions conserve normalized value Use probe condition: Merkle-free yield accounting route; amount case available liquidity plus 1 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.
