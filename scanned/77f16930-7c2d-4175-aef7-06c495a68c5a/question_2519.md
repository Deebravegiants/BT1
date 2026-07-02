# Q2519: getAssetCurrentLimit Buffer Over Reservation Distribution Loop Lido P2519

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and create queued withdrawal state that makes buffer reserve more than actual liabilities, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that stale buffers cannot permanently freeze free liquidity; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to block stuffing? Probe condition: Lido stETH unstake route; amount case 1 gwei; timing exactly at daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: create queued withdrawal state that makes buffer reserve more than actual liabilities; validation style: a local supported-token harness with configurable transfer behavior; probe condition: Lido stETH unstake route; amount case 1 gwei; timing exactly at daily reset; caller model EOA caller
- Exploit idea: Use malicious ERC20 harness to exercise the buffer over-reservation path against getAssetCurrentLimit and look for distribution loop breaking value conservation or liveness.
- Invariant to test: stale buffers cannot permanently freeze free liquidity; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Low. Block stuffing
- Fast validation: measure loops over nodeDelegatorQueue/user queues and assert bounded gas under max configured counts Use probe condition: Lido stETH unstake route; amount case 1 gwei; timing exactly at daily reset; caller model EOA caller.
