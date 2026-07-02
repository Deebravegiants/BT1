# Q2356: getAssetCurrentLimit Direct ETH Donation Skew Distribution Loop queued P2356

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and send ETH directly to permissive receive-style functions before an accounting read, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that donated ETH cannot be converted into attacker-owned principal beyond the donated amount; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to block stuffing? Probe condition: queued buffer route; amount case available liquidity plus 1 wei; timing one second before daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: send ETH directly to permissive receive-style functions before an accounting read; validation style: a fork test using current deployed balances and supported assets; probe condition: queued buffer route; amount case available liquidity plus 1 wei; timing one second before daily reset; caller model EOA caller
- Exploit idea: Use forked-mainnet state to exercise the direct ETH donation skew path against getAssetCurrentLimit and look for distribution loop breaking value conservation or liveness.
- Invariant to test: donated ETH cannot be converted into attacker-owned principal beyond the donated amount; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Low. Block stuffing
- Fast validation: measure loops over nodeDelegatorQueue/user queues and assert bounded gas under max configured counts Use probe condition: queued buffer route; amount case available liquidity plus 1 wei; timing one second before daily reset; caller model EOA caller.
