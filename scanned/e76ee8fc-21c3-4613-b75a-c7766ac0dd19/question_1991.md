# Q1991: getRsETHAmountToMint Fee On Transfer Token Skew Stale Price EigenLayer P1991

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)` while controlling asset, amount, minRSETHAmountExpected and transaction ordering and use a supported ERC20 path where received balance is lower than depositAmount or transfer amount, causing `contracts/LRTDepositPool.sol::getRsETHAmountToMint` to break the invariant that minted rsETH and committed withdrawals are based on actual assets received; specifically, stale price must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint, leading to direct theft of user funds? Probe condition: EigenLayer queued-withdrawal route; amount case deposit limit plus 1 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getRsETHAmountToMint
- Entrypoint: depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)
- Attacker controls: asset, amount, minRSETHAmountExpected and transaction ordering; scenario: use a supported ERC20 path where received balance is lower than depositAmount or transfer amount; validation style: a local supported-token harness with configurable transfer behavior; probe condition: EigenLayer queued-withdrawal route; amount case deposit limit plus 1 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller
- Exploit idea: Use malicious ERC20 harness to exercise the fee-on-transfer token skew path against getRsETHAmountToMint and look for stale price breaking value conservation or liveness.
- Invariant to test: minted rsETH and committed withdrawals are based on actual assets received; specifically, stale price must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint
- Expected Immunefi impact: Critical. Direct theft of any user funds, whether at-rest or in-motion, other than unclaimed yield
- Fast validation: sequence price update/deposit/withdraw with stale and fresh prices and assert no profitable round trip. Use probe condition: EigenLayer queued-withdrawal route; amount case deposit limit plus 1 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.
