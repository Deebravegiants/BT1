# Q2562: getAssetCurrentLimit Gas Amplified Loop Distribution Loop stETH P2562

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and grow a user-controlled queue/list then trigger a function that iterates it in a critical flow, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that user-controlled growth remains bounded and cannot cause unbounded gas consumption; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to temporary freezing of funds? Probe condition: stETH supported asset route; amount case 0.1 ether; timing exactly at daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: grow a user-controlled queue/list then trigger a function that iterates it in a critical flow; validation style: compare many dust calls against one large call; probe condition: stETH supported asset route; amount case 0.1 ether; timing exactly at daily reset; caller model EOA caller
- Exploit idea: Use dust-to-large differential to exercise the gas-amplified loop path against getAssetCurrentLimit and look for distribution loop breaking value conservation or liveness.
- Invariant to test: user-controlled growth remains bounded and cannot cause unbounded gas consumption; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: measure loops over nodeDelegatorQueue/user queues and assert bounded gas under max configured counts Use probe condition: stETH supported asset route; amount case 0.1 ether; timing exactly at daily reset; caller model EOA caller.
