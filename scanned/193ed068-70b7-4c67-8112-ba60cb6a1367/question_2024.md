# Q2024: getRsETHAmountToMint Pause Boundary Race Stale Price rsETH P2024

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)` while controlling asset, amount, minRSETHAmountExpected and transaction ordering and race a public action around a pause or public price-triggered pause transition, causing `contracts/LRTDepositPool.sol::getRsETHAmountToMint` to break the invariant that paused state cannot leave assets burned, committed, or transferred without corresponding settlement; specifically, stale price must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint, leading to direct theft of user funds? Probe condition: rsETH burn route; amount case 2 wei; timing one second before daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getRsETHAmountToMint
- Entrypoint: depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)
- Attacker controls: asset, amount, minRSETHAmountExpected and transaction ordering; scenario: race a public action around a pause or public price-triggered pause transition; validation style: compare ETH, stETH, and ETHx branches under the same value; probe condition: rsETH burn route; amount case 2 wei; timing one second before daily reset; caller model EOA caller
- Exploit idea: Use asset pair differential to exercise the pause boundary race path against getRsETHAmountToMint and look for stale price breaking value conservation or liveness.
- Invariant to test: paused state cannot leave assets burned, committed, or transferred without corresponding settlement; specifically, stale price must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint
- Expected Immunefi impact: Critical. Direct theft of any user funds, whether at-rest or in-motion, other than unclaimed yield
- Fast validation: sequence price update/deposit/withdraw with stale and fresh prices and assert no profitable round trip. Use probe condition: rsETH burn route; amount case 2 wei; timing one second before daily reset; caller model EOA caller.
