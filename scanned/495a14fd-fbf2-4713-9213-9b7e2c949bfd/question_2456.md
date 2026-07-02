# Q2456: getAssetCurrentLimit Oracle Decimal Mismatch Distribution Loop queued P2456

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and choose an asset flow whose oracle precision differs from 1e18 assumptions, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that all share/asset conversions preserve value despite decimals; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to block stuffing? Probe condition: queued buffer route; amount case minAmount minus 1 wei; timing exactly at daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: choose an asset flow whose oracle precision differs from 1e18 assumptions; validation style: compare ETH, stETH, and ETHx branches under the same value; probe condition: queued buffer route; amount case minAmount minus 1 wei; timing exactly at daily reset; caller model EOA caller
- Exploit idea: Use asset pair differential to exercise the oracle decimal mismatch path against getAssetCurrentLimit and look for distribution loop breaking value conservation or liveness.
- Invariant to test: all share/asset conversions preserve value despite decimals; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Low. Block stuffing
- Fast validation: measure loops over nodeDelegatorQueue/user queues and assert bounded gas under max configured counts Use probe condition: queued buffer route; amount case minAmount minus 1 wei; timing exactly at daily reset; caller model EOA caller.
