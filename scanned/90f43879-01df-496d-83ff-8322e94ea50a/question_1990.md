# Q1990: getRsETHAmountToMint Fee On Transfer Token Skew Oracle NodeDelegator P1990

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)` while controlling asset, amount, minRSETHAmountExpected and transaction ordering and use a supported ERC20 path where received balance is lower than depositAmount or transfer amount, causing `contracts/LRTDepositPool.sol::getRsETHAmountToMint` to break the invariant that minted rsETH and committed withdrawals are based on actual assets received; specifically, oracle must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint, leading to failure to deliver promised returns without principal loss? Probe condition: NodeDelegator pod-share route; amount case deposit limit plus 1 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getRsETHAmountToMint
- Entrypoint: depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)
- Attacker controls: asset, amount, minRSETHAmountExpected and transaction ordering; scenario: use a supported ERC20 path where received balance is lower than depositAmount or transfer amount; validation style: stateful fuzzing over deposit, update price, withdraw, unlock, complete; probe condition: NodeDelegator pod-share route; amount case deposit limit plus 1 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller
- Exploit idea: Use stateful invariant fuzz to exercise the fee-on-transfer token skew path against getRsETHAmountToMint and look for oracle breaking value conservation or liveness.
- Invariant to test: minted rsETH and committed withdrawals are based on actual assets received; specifically, oracle must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: mock the configured price fetcher within sane bounds and assert conversions conserve normalized value Use probe condition: NodeDelegator pod-share route; amount case deposit limit plus 1 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.
