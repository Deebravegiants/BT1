# Q2337: getAssetCurrentLimit Round Up Insolvency Distribution Loop daily P2337

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and choose amounts just above precision boundaries so liabilities round up while assets round down, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that rsETH liabilities never exceed normalized protocol assets; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to temporary freezing of funds? Probe condition: daily mint limit route; amount case available liquidity exactly; timing one second before daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: choose amounts just above precision boundaries so liabilities round up while assets round down; validation style: warp/block-roll around day or withdrawal-delay boundaries; probe condition: daily mint limit route; amount case available liquidity exactly; timing one second before daily reset; caller model EOA caller
- Exploit idea: Use period boundary fuzz to exercise the round-up insolvency path against getAssetCurrentLimit and look for distribution loop breaking value conservation or liveness.
- Invariant to test: rsETH liabilities never exceed normalized protocol assets; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: measure loops over nodeDelegatorQueue/user queues and assert bounded gas under max configured counts Use probe condition: daily mint limit route; amount case available liquidity exactly; timing one second before daily reset; caller model EOA caller.
