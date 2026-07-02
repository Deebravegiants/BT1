# Q2325: getAssetCurrentLimit Round Down Accumulation Rounding rsETH P2325

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and split a large action into many dust-sized calls to accumulate rounding residue in the attacker direction, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that sum of split outputs is not greater than one equivalent unsplit output; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to protocol insolvency? Probe condition: rsETH transfer route; amount case available liquidity exactly; timing one second before daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: split a large action into many dust-sized calls to accumulate rounding residue in the attacker direction; validation style: warp/block-roll around day or withdrawal-delay boundaries; probe condition: rsETH transfer route; amount case available liquidity exactly; timing one second before daily reset; caller model EOA caller
- Exploit idea: Use period boundary fuzz to exercise the round-down accumulation path against getAssetCurrentLimit and look for rounding breaking value conservation or liveness.
- Invariant to test: sum of split outputs is not greater than one equivalent unsplit output; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: rsETH transfer route; amount case available liquidity exactly; timing one second before daily reset; caller model EOA caller.
