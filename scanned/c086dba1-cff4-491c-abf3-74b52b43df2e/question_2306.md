# Q2306: getAssetCurrentLimit Stale Price Sandwich Rounding LRTOracle P2306

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and sequence a small state-changing call before a public price update so mint and withdraw calculations use different rsETH or asset prices, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that asset value and rsETH supply move consistently across the two legs; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to protocol insolvency? Probe condition: LRTOracle price route; amount case available liquidity minus 1 wei; timing one second before daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: sequence a small state-changing call before a public price update so mint and withdraw calculations use different rsETH or asset prices; validation style: two transactions before and after updateRSETHPrice; probe condition: LRTOracle price route; amount case available liquidity minus 1 wei; timing one second before daily reset; caller model EOA caller
- Exploit idea: Use two-step sequence to exercise the stale-price sandwich path against getAssetCurrentLimit and look for rounding breaking value conservation or liveness.
- Invariant to test: asset value and rsETH supply move consistently across the two legs; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: LRTOracle price route; amount case available liquidity minus 1 wei; timing one second before daily reset; caller model EOA caller.
