# Q2386: getAssetCurrentLimit Rebasing Balance Drift Distribution Loop LRTOracle P2386

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and let a supported rebasing LST balance change between request creation and final settlement, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that rebases cannot create unbacked rsETH or freeze queued withdrawals; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to block stuffing? Probe condition: LRTOracle price route; amount case deposit limit plus 1 wei; timing one second before daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: let a supported rebasing LST balance change between request creation and final settlement; validation style: stateful fuzzing over deposit, update price, withdraw, unlock, complete; probe condition: LRTOracle price route; amount case deposit limit plus 1 wei; timing one second before daily reset; caller model EOA caller
- Exploit idea: Use stateful invariant fuzz to exercise the rebasing balance drift path against getAssetCurrentLimit and look for distribution loop breaking value conservation or liveness.
- Invariant to test: rebases cannot create unbacked rsETH or freeze queued withdrawals; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Low. Block stuffing
- Fast validation: measure loops over nodeDelegatorQueue/user queues and assert bounded gas under max configured counts Use probe condition: LRTOracle price route; amount case deposit limit plus 1 wei; timing one second before daily reset; caller model EOA caller.
