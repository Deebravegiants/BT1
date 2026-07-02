# Q2114: getRsETHAmountToMint Buffer Under Reservation Rounding deposit-limit P2114

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)` while controlling asset, amount, minRSETHAmountExpected and transaction ordering and create instant withdrawal demand while queued withdrawal buffer is stale or too low, causing `contracts/LRTDepositPool.sol::getRsETHAmountToMint` to break the invariant that instant withdrawals cannot consume assets reserved for queued users; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint, leading to failure to deliver promised returns without principal loss? Probe condition: deposit-limit accounting route; amount case 1 gwei; timing one second before daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getRsETHAmountToMint
- Entrypoint: depositETH/depositAsset calls getRsETHAmountToMint(asset, amount)
- Attacker controls: asset, amount, minRSETHAmountExpected and transaction ordering; scenario: create instant withdrawal demand while queued withdrawal buffer is stale or too low; validation style: two transactions before and after updateRSETHPrice; probe condition: deposit-limit accounting route; amount case 1 gwei; timing one second before daily reset; caller model EOA caller
- Exploit idea: Use two-step sequence to exercise the buffer under-reservation path against getRsETHAmountToMint and look for rounding breaking value conservation or liveness.
- Invariant to test: instant withdrawals cannot consume assets reserved for queued users; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getRsETHAmountToMint
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: deposit-limit accounting route; amount case 1 gwei; timing one second before daily reset; caller model EOA caller.
