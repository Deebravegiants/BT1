# Q2295: getRsETHAmountToMint Block Timestamp Boundary Rounding withdrawal P2295

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)` while controlling asset, amount, minRSETHAmountExpected and transaction ordering and execute calls exactly at delay, daily reset, or period boundary blocks, causing `contracts/LRTDepositPool.sol::getRsETHAmountToMint` to break the invariant that boundary equality cannot bypass delay, limits, or settlement ordering; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint, leading to direct theft of user funds? Probe condition: withdrawal request nonce route; amount case daily limit exactly; timing one second before daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getRsETHAmountToMint
- Entrypoint: depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)
- Attacker controls: asset, amount, minRSETHAmountExpected and transaction ordering; scenario: execute calls exactly at delay, daily reset, or period boundary blocks; validation style: a helper contract batching allowed public calls; probe condition: withdrawal request nonce route; amount case daily limit exactly; timing one second before daily reset; caller model EOA caller
- Exploit idea: Use batched multicall-style sequence to exercise the block-timestamp boundary path against getRsETHAmountToMint and look for rounding breaking value conservation or liveness.
- Invariant to test: boundary equality cannot bypass delay, limits, or settlement ordering; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint
- Expected Immunefi impact: Critical. Direct theft of any user funds, whether at-rest or in-motion, other than unclaimed yield
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: withdrawal request nonce route; amount case daily limit exactly; timing one second before daily reset; caller model EOA caller.
