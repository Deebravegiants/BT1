# Q2027: getRsETHAmountToMint Pause Boundary Race Oracle FeeReceiver P2027

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)` while controlling asset, amount, minRSETHAmountExpected and transaction ordering and race a public action around a pause or public price-triggered pause transition, causing `contracts/LRTDepositPool.sol::getRsETHAmountToMint` to break the invariant that paused state cannot leave assets burned, committed, or transferred without corresponding settlement; specifically, oracle must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint, leading to direct theft of user funds? Probe condition: FeeReceiver reward route; amount case 2 wei; timing one second before daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getRsETHAmountToMint
- Entrypoint: depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)
- Attacker controls: asset, amount, minRSETHAmountExpected and transaction ordering; scenario: race a public action around a pause or public price-triggered pause transition; validation style: a local supported-token harness with configurable transfer behavior; probe condition: FeeReceiver reward route; amount case 2 wei; timing one second before daily reset; caller model EOA caller
- Exploit idea: Use malicious ERC20 harness to exercise the pause boundary race path against getRsETHAmountToMint and look for oracle breaking value conservation or liveness.
- Invariant to test: paused state cannot leave assets burned, committed, or transferred without corresponding settlement; specifically, oracle must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint
- Expected Immunefi impact: Critical. Direct theft of any user funds, whether at-rest or in-motion, other than unclaimed yield
- Fast validation: mock the configured price fetcher within sane bounds and assert conversions conserve normalized value Use probe condition: FeeReceiver reward route; amount case 2 wei; timing one second before daily reset; caller model EOA caller.
