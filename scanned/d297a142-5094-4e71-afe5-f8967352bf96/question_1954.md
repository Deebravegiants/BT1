# Q1954: getRsETHAmountToMint Round Up Insolvency Stale Price deposit-limit P1954

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)` while controlling asset, amount, minRSETHAmountExpected and transaction ordering and choose amounts just above precision boundaries so liabilities round up while assets round down, causing `contracts/LRTDepositPool.sol::getRsETHAmountToMint` to break the invariant that rsETH liabilities never exceed normalized protocol assets; specifically, stale price must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint, leading to failure to deliver promised returns without principal loss? Probe condition: deposit-limit accounting route; amount case available liquidity plus 1 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getRsETHAmountToMint
- Entrypoint: depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)
- Attacker controls: asset, amount, minRSETHAmountExpected and transaction ordering; scenario: choose amounts just above precision boundaries so liabilities round up while assets round down; validation style: stateful fuzzing over deposit, update price, withdraw, unlock, complete; probe condition: deposit-limit accounting route; amount case available liquidity plus 1 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller
- Exploit idea: Use stateful invariant fuzz to exercise the round-up insolvency path against getRsETHAmountToMint and look for stale price breaking value conservation or liveness.
- Invariant to test: rsETH liabilities never exceed normalized protocol assets; specifically, stale price must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: sequence price update/deposit/withdraw with stale and fresh prices and assert no profitable round trip. Use probe condition: deposit-limit accounting route; amount case available liquidity plus 1 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.
