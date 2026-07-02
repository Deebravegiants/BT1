# Q2502: getAssetCurrentLimit Buffer Under Reservation Rounding stETH P2502

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and create instant withdrawal demand while queued withdrawal buffer is stale or too low, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that instant withdrawals cannot consume assets reserved for queued users; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to protocol insolvency? Probe condition: stETH supported asset route; amount case 1 gwei; timing exactly at daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: create instant withdrawal demand while queued withdrawal buffer is stale or too low; validation style: compare many dust calls against one large call; probe condition: stETH supported asset route; amount case 1 gwei; timing exactly at daily reset; caller model EOA caller
- Exploit idea: Use dust-to-large differential to exercise the buffer under-reservation path against getAssetCurrentLimit and look for rounding breaking value conservation or liveness.
- Invariant to test: instant withdrawals cannot consume assets reserved for queued users; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: stETH supported asset route; amount case 1 gwei; timing exactly at daily reset; caller model EOA caller.
