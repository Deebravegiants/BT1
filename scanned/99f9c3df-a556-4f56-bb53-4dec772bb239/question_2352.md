# Q2352: getAssetCurrentLimit Zero Or Dust Edge Distribution Loop Aave P2352

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and use zero-like, one-wei, or min-threshold-adjacent amounts to bypass accounting updates, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that dust inputs cannot create withdrawable value or stuck committed assets; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to temporary freezing of funds? Probe condition: Aave aWETH liquidity route; amount case available liquidity plus 1 wei; timing one second before daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: use zero-like, one-wei, or min-threshold-adjacent amounts to bypass accounting updates; validation style: attacker-created state followed by an honest operator action; probe condition: Aave aWETH liquidity route; amount case available liquidity plus 1 wei; timing one second before daily reset; caller model EOA caller
- Exploit idea: Use operator-normalization follow-up to exercise the zero-or-dust edge path against getAssetCurrentLimit and look for distribution loop breaking value conservation or liveness.
- Invariant to test: dust inputs cannot create withdrawable value or stuck committed assets; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: measure loops over nodeDelegatorQueue/user queues and assert bounded gas under max configured counts Use probe condition: Aave aWETH liquidity route; amount case available liquidity plus 1 wei; timing one second before daily reset; caller model EOA caller.
