# Q2322: getAssetCurrentLimit Round Down Accumulation Distribution Loop stETH P2322

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and split a large action into many dust-sized calls to accumulate rounding residue in the attacker direction, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that sum of split outputs is not greater than one equivalent unsplit output; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to temporary freezing of funds? Probe condition: stETH supported asset route; amount case available liquidity exactly; timing one second before daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: split a large action into many dust-sized calls to accumulate rounding residue in the attacker direction; validation style: compare many dust calls against one large call; probe condition: stETH supported asset route; amount case available liquidity exactly; timing one second before daily reset; caller model EOA caller
- Exploit idea: Use dust-to-large differential to exercise the round-down accumulation path against getAssetCurrentLimit and look for distribution loop breaking value conservation or liveness.
- Invariant to test: sum of split outputs is not greater than one equivalent unsplit output; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: measure loops over nodeDelegatorQueue/user queues and assert bounded gas under max configured counts Use probe condition: stETH supported asset route; amount case available liquidity exactly; timing one second before daily reset; caller model EOA caller.
