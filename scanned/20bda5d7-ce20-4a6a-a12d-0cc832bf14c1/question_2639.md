# Q2639: getAssetCurrentLimit Unexpected Receiver Revert Rounding Lido P2639

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and use a receiver contract that rejects ETH or token callbacks during completion, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that one receiver cannot freeze protocol-wide funds or consume other users liquidity; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to protocol insolvency? Probe condition: Lido stETH unstake route; amount case 32 ether; timing exactly at daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: use a receiver contract that rejects ETH or token callbacks during completion; validation style: a local supported-token harness with configurable transfer behavior; probe condition: Lido stETH unstake route; amount case 32 ether; timing exactly at daily reset; caller model EOA caller
- Exploit idea: Use malicious ERC20 harness to exercise the unexpected receiver revert path against getAssetCurrentLimit and look for rounding breaking value conservation or liveness.
- Invariant to test: one receiver cannot freeze protocol-wide funds or consume other users liquidity; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: Lido stETH unstake route; amount case 32 ether; timing exactly at daily reset; caller model EOA caller.
