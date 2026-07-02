# Q1974: getRsETHAmountToMint Direct ETH Donation Skew Rounding deposit-limit P1974

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)` while controlling asset, amount, minRSETHAmountExpected and transaction ordering and send ETH directly to permissive receive-style functions before an accounting read, causing `contracts/LRTDepositPool.sol::getRsETHAmountToMint` to break the invariant that donated ETH cannot be converted into attacker-owned principal beyond the donated amount; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint, leading to direct theft of user funds? Probe condition: deposit-limit accounting route; amount case deposit limit minus 1 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getRsETHAmountToMint
- Entrypoint: depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)
- Attacker controls: asset, amount, minRSETHAmountExpected and transaction ordering; scenario: send ETH directly to permissive receive-style functions before an accounting read; validation style: compare many dust calls against one large call; probe condition: deposit-limit accounting route; amount case deposit limit minus 1 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller
- Exploit idea: Use dust-to-large differential to exercise the direct ETH donation skew path against getRsETHAmountToMint and look for rounding breaking value conservation or liveness.
- Invariant to test: donated ETH cannot be converted into attacker-owned principal beyond the donated amount; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint
- Expected Immunefi impact: Critical. Direct theft of any user funds, whether at-rest or in-motion, other than unclaimed yield
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: deposit-limit accounting route; amount case deposit limit minus 1 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.
