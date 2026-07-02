# Q2632: getAssetCurrentLimit Unexpected Receiver Revert Distribution Loop Aave P2632

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and use a receiver contract that rejects ETH or token callbacks during completion, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that one receiver cannot freeze protocol-wide funds or consume other users liquidity; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to temporary freezing of funds? Probe condition: Aave aWETH liquidity route; amount case 32 ether; timing exactly at daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: use a receiver contract that rejects ETH or token callbacks during completion; validation style: a fork test using current deployed balances and supported assets; probe condition: Aave aWETH liquidity route; amount case 32 ether; timing exactly at daily reset; caller model EOA caller
- Exploit idea: Use forked-mainnet state to exercise the unexpected receiver revert path against getAssetCurrentLimit and look for distribution loop breaking value conservation or liveness.
- Invariant to test: one receiver cannot freeze protocol-wide funds or consume other users liquidity; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: measure loops over nodeDelegatorQueue/user queues and assert bounded gas under max configured counts Use probe condition: Aave aWETH liquidity route; amount case 32 ether; timing exactly at daily reset; caller model EOA caller.
