# Q2505: getAssetCurrentLimit Buffer Under Reservation Deposit Limit rsETH P2505

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and create instant withdrawal demand while queued withdrawal buffer is stale or too low, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that instant withdrawals cannot consume assets reserved for queued users; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to permanent freezing of funds? Probe condition: rsETH transfer route; amount case 1 gwei; timing exactly at daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: create instant withdrawal demand while queued withdrawal buffer is stale or too low; validation style: warp/block-roll around day or withdrawal-delay boundaries; probe condition: rsETH transfer route; amount case 1 gwei; timing exactly at daily reset; caller model EOA caller
- Exploit idea: Use period boundary fuzz to exercise the buffer under-reservation path against getAssetCurrentLimit and look for deposit limit breaking value conservation or liveness.
- Invariant to test: instant withdrawals cannot consume assets reserved for queued users; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: fuzz deposits around getAssetCurrentLimit and assert total deposits never exceed the configured limit by more than intended rounding Use probe condition: rsETH transfer route; amount case 1 gwei; timing exactly at daily reset; caller model EOA caller.
