# Q2115: getRsETHAmountToMint Buffer Under Reservation Oracle withdrawal P2115

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)` while controlling asset, amount, minRSETHAmountExpected and transaction ordering and create instant withdrawal demand while queued withdrawal buffer is stale or too low, causing `contracts/LRTDepositPool.sol::getRsETHAmountToMint` to break the invariant that instant withdrawals cannot consume assets reserved for queued users; specifically, oracle must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint, leading to direct theft of user funds? Probe condition: withdrawal request nonce route; amount case 1 gwei; timing one second before daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getRsETHAmountToMint
- Entrypoint: depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)
- Attacker controls: asset, amount, minRSETHAmountExpected and transaction ordering; scenario: create instant withdrawal demand while queued withdrawal buffer is stale or too low; validation style: a helper contract batching allowed public calls; probe condition: withdrawal request nonce route; amount case 1 gwei; timing one second before daily reset; caller model EOA caller
- Exploit idea: Use batched multicall-style sequence to exercise the buffer under-reservation path against getRsETHAmountToMint and look for oracle breaking value conservation or liveness.
- Invariant to test: instant withdrawals cannot consume assets reserved for queued users; specifically, oracle must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint
- Expected Immunefi impact: Critical. Direct theft of any user funds, whether at-rest or in-motion, other than unclaimed yield
- Fast validation: mock the configured price fetcher within sane bounds and assert conversions conserve normalized value Use probe condition: withdrawal request nonce route; amount case 1 gwei; timing one second before daily reset; caller model EOA caller.
