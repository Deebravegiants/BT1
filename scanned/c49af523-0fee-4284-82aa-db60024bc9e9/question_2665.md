# Q2665: getAssetCurrentLimit Unclaimed Yield Diversion Distribution Loop rsETH P2665

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and time reward send, interest collection, fee minting, or claim settlement to redirect yield, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that unclaimed yield cannot be stolen or permanently frozen by a public caller; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to temporary freezing of funds? Probe condition: rsETH transfer route; amount case daily limit minus 1 wei; timing exactly at daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: time reward send, interest collection, fee minting, or claim settlement to redirect yield; validation style: one transaction using a contract wallet and controlled calldata; probe condition: rsETH transfer route; amount case daily limit minus 1 wei; timing exactly at daily reset; caller model EOA caller
- Exploit idea: Use single transaction to exercise the unclaimed-yield diversion path against getAssetCurrentLimit and look for distribution loop breaking value conservation or liveness.
- Invariant to test: unclaimed yield cannot be stolen or permanently frozen by a public caller; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: measure loops over nodeDelegatorQueue/user queues and assert bounded gas under max configured counts Use probe condition: rsETH transfer route; amount case daily limit minus 1 wei; timing exactly at daily reset; caller model EOA caller.
