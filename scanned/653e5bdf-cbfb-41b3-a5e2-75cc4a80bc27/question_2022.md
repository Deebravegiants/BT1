# Q2022: getRsETHAmountToMint Pause Boundary Race Rounding stETH P2022

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)` while controlling asset, amount, minRSETHAmountExpected and transaction ordering and race a public action around a pause or public price-triggered pause transition, causing `contracts/LRTDepositPool.sol::getRsETHAmountToMint` to break the invariant that paused state cannot leave assets burned, committed, or transferred without corresponding settlement; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint, leading to protocol insolvency? Probe condition: stETH supported asset route; amount case 2 wei; timing one second before daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getRsETHAmountToMint
- Entrypoint: depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)
- Attacker controls: asset, amount, minRSETHAmountExpected and transaction ordering; scenario: race a public action around a pause or public price-triggered pause transition; validation style: compare many dust calls against one large call; probe condition: stETH supported asset route; amount case 2 wei; timing one second before daily reset; caller model EOA caller
- Exploit idea: Use dust-to-large differential to exercise the pause boundary race path against getRsETHAmountToMint and look for rounding breaking value conservation or liveness.
- Invariant to test: paused state cannot leave assets burned, committed, or transferred without corresponding settlement; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: stETH supported asset route; amount case 2 wei; timing one second before daily reset; caller model EOA caller.
