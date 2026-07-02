# Q2296: getRsETHAmountToMint Block Timestamp Boundary Oracle queued P2296

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)` while controlling asset, amount, minRSETHAmountExpected and transaction ordering and execute calls exactly at delay, daily reset, or period boundary blocks, causing `contracts/LRTDepositPool.sol::getRsETHAmountToMint` to break the invariant that boundary equality cannot bypass delay, limits, or settlement ordering; specifically, oracle must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint, leading to protocol insolvency? Probe condition: queued buffer route; amount case daily limit exactly; timing one second before daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getRsETHAmountToMint
- Entrypoint: depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)
- Attacker controls: asset, amount, minRSETHAmountExpected and transaction ordering; scenario: execute calls exactly at delay, daily reset, or period boundary blocks; validation style: a fork test using current deployed balances and supported assets; probe condition: queued buffer route; amount case daily limit exactly; timing one second before daily reset; caller model EOA caller
- Exploit idea: Use forked-mainnet state to exercise the block-timestamp boundary path against getRsETHAmountToMint and look for oracle breaking value conservation or liveness.
- Invariant to test: boundary equality cannot bypass delay, limits, or settlement ordering; specifically, oracle must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: mock the configured price fetcher within sane bounds and assert conversions conserve normalized value Use probe condition: queued buffer route; amount case daily limit exactly; timing one second before daily reset; caller model EOA caller.
