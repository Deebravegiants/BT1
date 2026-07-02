# Q2123: getRsETHAmountToMint Buffer Under Reservation Oracle ETHx P2123

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)` while controlling asset, amount, minRSETHAmountExpected and transaction ordering and create instant withdrawal demand while queued withdrawal buffer is stale or too low, causing `contracts/LRTDepositPool.sol::getRsETHAmountToMint` to break the invariant that instant withdrawals cannot consume assets reserved for queued users; specifically, oracle must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint, leading to failure to deliver promised returns without principal loss? Probe condition: ETHx supported asset route; amount case 0.001 ether; timing one second before daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getRsETHAmountToMint
- Entrypoint: depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)
- Attacker controls: asset, amount, minRSETHAmountExpected and transaction ordering; scenario: create instant withdrawal demand while queued withdrawal buffer is stale or too low; validation style: a local supported-token harness with configurable transfer behavior; probe condition: ETHx supported asset route; amount case 0.001 ether; timing one second before daily reset; caller model EOA caller
- Exploit idea: Use malicious ERC20 harness to exercise the buffer under-reservation path against getRsETHAmountToMint and look for oracle breaking value conservation or liveness.
- Invariant to test: instant withdrawals cannot consume assets reserved for queued users; specifically, oracle must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: mock the configured price fetcher within sane bounds and assert conversions conserve normalized value Use probe condition: ETHx supported asset route; amount case 0.001 ether; timing one second before daily reset; caller model EOA caller.
