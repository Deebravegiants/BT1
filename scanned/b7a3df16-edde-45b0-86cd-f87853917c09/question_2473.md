# Q2473: getAssetCurrentLimit Fee Mint Limit Boundary Distribution Loop Merkle-free P2473

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and execute price updates at exactly fee-period or mint-period boundaries, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that daily limits cannot be bypassed or permanently block legitimate minting; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to temporary freezing of funds? Probe condition: Merkle-free yield accounting route; amount case exact minAmount; timing exactly at daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: execute price updates at exactly fee-period or mint-period boundaries; validation style: one transaction using a contract wallet and controlled calldata; probe condition: Merkle-free yield accounting route; amount case exact minAmount; timing exactly at daily reset; caller model EOA caller
- Exploit idea: Use single transaction to exercise the fee mint limit boundary path against getAssetCurrentLimit and look for distribution loop breaking value conservation or liveness.
- Invariant to test: daily limits cannot be bypassed or permanently block legitimate minting; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: measure loops over nodeDelegatorQueue/user queues and assert bounded gas under max configured counts Use probe condition: Merkle-free yield accounting route; amount case exact minAmount; timing exactly at daily reset; caller model EOA caller.
