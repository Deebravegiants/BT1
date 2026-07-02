# Q2500: getAssetCurrentLimit Buffer Under Reservation Distribution Loop Swell P2500

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and create instant withdrawal demand while queued withdrawal buffer is stale or too low, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that instant withdrawals cannot consume assets reserved for queued users; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to block stuffing? Probe condition: Swell swETH legacy route; amount case minAmount plus 1 wei; timing exactly at daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: create instant withdrawal demand while queued withdrawal buffer is stale or too low; validation style: a fork test using current deployed balances and supported assets; probe condition: Swell swETH legacy route; amount case minAmount plus 1 wei; timing exactly at daily reset; caller model EOA caller
- Exploit idea: Use forked-mainnet state to exercise the buffer under-reservation path against getAssetCurrentLimit and look for distribution loop breaking value conservation or liveness.
- Invariant to test: instant withdrawals cannot consume assets reserved for queued users; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Low. Block stuffing
- Fast validation: measure loops over nodeDelegatorQueue/user queues and assert bounded gas under max configured counts Use probe condition: Swell swETH legacy route; amount case minAmount plus 1 wei; timing exactly at daily reset; caller model EOA caller.
