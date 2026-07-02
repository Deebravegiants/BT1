# Q1970: getRsETHAmountToMint Direct ETH Donation Skew Rounding NodeDelegator P1970

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)` while controlling asset, amount, minRSETHAmountExpected and transaction ordering and send ETH directly to permissive receive-style functions before an accounting read, causing `contracts/LRTDepositPool.sol::getRsETHAmountToMint` to break the invariant that donated ETH cannot be converted into attacker-owned principal beyond the donated amount; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint, leading to failure to deliver promised returns without principal loss? Probe condition: NodeDelegator pod-share route; amount case deposit limit minus 1 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getRsETHAmountToMint
- Entrypoint: depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)
- Attacker controls: asset, amount, minRSETHAmountExpected and transaction ordering; scenario: send ETH directly to permissive receive-style functions before an accounting read; validation style: two transactions before and after updateRSETHPrice; probe condition: NodeDelegator pod-share route; amount case deposit limit minus 1 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller
- Exploit idea: Use two-step sequence to exercise the direct ETH donation skew path against getRsETHAmountToMint and look for rounding breaking value conservation or liveness.
- Invariant to test: donated ETH cannot be converted into attacker-owned principal beyond the donated amount; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: NodeDelegator pod-share route; amount case deposit limit minus 1 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.
