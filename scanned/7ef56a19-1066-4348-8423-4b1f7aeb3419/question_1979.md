# Q1979: getRsETHAmountToMint Direct ETH Donation Skew Oracle Lido P1979

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)` while controlling asset, amount, minRSETHAmountExpected and transaction ordering and send ETH directly to permissive receive-style functions before an accounting read, causing `contracts/LRTDepositPool.sol::getRsETHAmountToMint` to break the invariant that donated ETH cannot be converted into attacker-owned principal beyond the donated amount; specifically, oracle must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint, leading to failure to deliver promised returns without principal loss? Probe condition: Lido stETH unstake route; amount case deposit limit minus 1 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getRsETHAmountToMint
- Entrypoint: depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)
- Attacker controls: asset, amount, minRSETHAmountExpected and transaction ordering; scenario: send ETH directly to permissive receive-style functions before an accounting read; validation style: a local supported-token harness with configurable transfer behavior; probe condition: Lido stETH unstake route; amount case deposit limit minus 1 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller
- Exploit idea: Use malicious ERC20 harness to exercise the direct ETH donation skew path against getRsETHAmountToMint and look for oracle breaking value conservation or liveness.
- Invariant to test: donated ETH cannot be converted into attacker-owned principal beyond the donated amount; specifically, oracle must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: mock the configured price fetcher within sane bounds and assert conversions conserve normalized value Use probe condition: Lido stETH unstake route; amount case deposit limit minus 1 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.
