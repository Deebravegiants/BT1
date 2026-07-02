# Q2561: getAssetCurrentLimit Gas Amplified Loop Rounding ETH P2561

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and grow a user-controlled queue/list then trigger a function that iterates it in a critical flow, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that user-controlled growth remains bounded and cannot cause unbounded gas consumption; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to protocol insolvency? Probe condition: ETH sentinel route; amount case 0.1 ether; timing exactly at daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: grow a user-controlled queue/list then trigger a function that iterates it in a critical flow; validation style: several attacker accounts creating adjacent requests; probe condition: ETH sentinel route; amount case 0.1 ether; timing exactly at daily reset; caller model EOA caller
- Exploit idea: Use multi-account queue pressure to exercise the gas-amplified loop path against getAssetCurrentLimit and look for rounding breaking value conservation or liveness.
- Invariant to test: user-controlled growth remains bounded and cannot cause unbounded gas consumption; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: ETH sentinel route; amount case 0.1 ether; timing exactly at daily reset; caller model EOA caller.
