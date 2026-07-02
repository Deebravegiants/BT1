# Q2638: getAssetCurrentLimit Unexpected Receiver Revert Deposit Limit daily P2638

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and use a receiver contract that rejects ETH or token callbacks during completion, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that one receiver cannot freeze protocol-wide funds or consume other users liquidity; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to permanent freezing of funds? Probe condition: daily fee mint limit route; amount case 32 ether; timing exactly at daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: use a receiver contract that rejects ETH or token callbacks during completion; validation style: stateful fuzzing over deposit, update price, withdraw, unlock, complete; probe condition: daily fee mint limit route; amount case 32 ether; timing exactly at daily reset; caller model EOA caller
- Exploit idea: Use stateful invariant fuzz to exercise the unexpected receiver revert path against getAssetCurrentLimit and look for deposit limit breaking value conservation or liveness.
- Invariant to test: one receiver cannot freeze protocol-wide funds or consume other users liquidity; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: fuzz deposits around getAssetCurrentLimit and assert total deposits never exceed the configured limit by more than intended rounding Use probe condition: daily fee mint limit route; amount case 32 ether; timing exactly at daily reset; caller model EOA caller.
