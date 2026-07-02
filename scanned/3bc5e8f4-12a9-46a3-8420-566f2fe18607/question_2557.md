# Q2557: getAssetCurrentLimit Gas Amplified Loop Rounding daily P2557

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and grow a user-controlled queue/list then trigger a function that iterates it in a critical flow, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that user-controlled growth remains bounded and cannot cause unbounded gas consumption; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to protocol insolvency? Probe condition: daily mint limit route; amount case 0.01 ether; timing exactly at daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: grow a user-controlled queue/list then trigger a function that iterates it in a critical flow; validation style: one transaction using a contract wallet and controlled calldata; probe condition: daily mint limit route; amount case 0.01 ether; timing exactly at daily reset; caller model EOA caller
- Exploit idea: Use single transaction to exercise the gas-amplified loop path against getAssetCurrentLimit and look for rounding breaking value conservation or liveness.
- Invariant to test: user-controlled growth remains bounded and cannot cause unbounded gas consumption; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: daily mint limit route; amount case 0.01 ether; timing exactly at daily reset; caller model EOA caller.
