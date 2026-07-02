# Q2336: getAssetCurrentLimit Round Up Insolvency Rounding queued P2336

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and choose amounts just above precision boundaries so liabilities round up while assets round down, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that rsETH liabilities never exceed normalized protocol assets; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to protocol insolvency? Probe condition: queued buffer route; amount case available liquidity exactly; timing one second before daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: choose amounts just above precision boundaries so liabilities round up while assets round down; validation style: compare ETH, stETH, and ETHx branches under the same value; probe condition: queued buffer route; amount case available liquidity exactly; timing one second before daily reset; caller model EOA caller
- Exploit idea: Use asset pair differential to exercise the round-up insolvency path against getAssetCurrentLimit and look for rounding breaking value conservation or liveness.
- Invariant to test: rsETH liabilities never exceed normalized protocol assets; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: queued buffer route; amount case available liquidity exactly; timing one second before daily reset; caller model EOA caller.
