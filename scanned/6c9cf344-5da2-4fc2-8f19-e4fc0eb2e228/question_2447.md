# Q2447: getAssetCurrentLimit FirstExcludedIndex Boundary Rounding FeeReceiver P2447

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and fill withdrawal requests around the unlockQueue firstExcludedIndex boundary, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that unlocking cannot skip, over-unlock, or permanently strand requests; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to protocol insolvency? Probe condition: FeeReceiver reward route; amount case minAmount minus 1 wei; timing exactly at daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: fill withdrawal requests around the unlockQueue firstExcludedIndex boundary; validation style: a local supported-token harness with configurable transfer behavior; probe condition: FeeReceiver reward route; amount case minAmount minus 1 wei; timing exactly at daily reset; caller model EOA caller
- Exploit idea: Use malicious ERC20 harness to exercise the firstExcludedIndex boundary path against getAssetCurrentLimit and look for rounding breaking value conservation or liveness.
- Invariant to test: unlocking cannot skip, over-unlock, or permanently strand requests; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: FeeReceiver reward route; amount case minAmount minus 1 wei; timing exactly at daily reset; caller model EOA caller.
