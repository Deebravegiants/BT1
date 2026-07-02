# Q2338: getAssetCurrentLimit Round Up Insolvency Distribution Loop daily P2338

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and choose amounts just above precision boundaries so liabilities round up while assets round down, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that rsETH liabilities never exceed normalized protocol assets; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to block stuffing? Probe condition: daily fee mint limit route; amount case available liquidity exactly; timing one second before daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: choose amounts just above precision boundaries so liabilities round up while assets round down; validation style: stateful fuzzing over deposit, update price, withdraw, unlock, complete; probe condition: daily fee mint limit route; amount case available liquidity exactly; timing one second before daily reset; caller model EOA caller
- Exploit idea: Use stateful invariant fuzz to exercise the round-up insolvency path against getAssetCurrentLimit and look for distribution loop breaking value conservation or liveness.
- Invariant to test: rsETH liabilities never exceed normalized protocol assets; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Low. Block stuffing
- Fast validation: measure loops over nodeDelegatorQueue/user queues and assert bounded gas under max configured counts Use probe condition: daily fee mint limit route; amount case available liquidity exactly; timing one second before daily reset; caller model EOA caller.
