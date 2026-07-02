# Q2676: getAssetCurrentLimit Unclaimed Yield Diversion Rounding queued P2676

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and time reward send, interest collection, fee minting, or claim settlement to redirect yield, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that unclaimed yield cannot be stolen or permanently frozen by a public caller; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to protocol insolvency? Probe condition: queued buffer route; amount case daily limit minus 1 wei; timing exactly at daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: time reward send, interest collection, fee minting, or claim settlement to redirect yield; validation style: attacker-created state followed by an honest operator action; probe condition: queued buffer route; amount case daily limit minus 1 wei; timing exactly at daily reset; caller model EOA caller
- Exploit idea: Use operator-normalization follow-up to exercise the unclaimed-yield diversion path against getAssetCurrentLimit and look for rounding breaking value conservation or liveness.
- Invariant to test: unclaimed yield cannot be stolen or permanently frozen by a public caller; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: queued buffer route; amount case daily limit minus 1 wei; timing exactly at daily reset; caller model EOA caller.
