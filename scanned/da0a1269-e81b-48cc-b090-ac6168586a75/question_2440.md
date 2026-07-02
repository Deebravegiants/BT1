# Q2440: getAssetCurrentLimit FirstExcludedIndex Boundary Distribution Loop Swell P2440

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and fill withdrawal requests around the unlockQueue firstExcludedIndex boundary, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that unlocking cannot skip, over-unlock, or permanently strand requests; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to temporary freezing of funds? Probe condition: Swell swETH legacy route; amount case 2 wei; timing exactly at daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: fill withdrawal requests around the unlockQueue firstExcludedIndex boundary; validation style: a fork test using current deployed balances and supported assets; probe condition: Swell swETH legacy route; amount case 2 wei; timing exactly at daily reset; caller model EOA caller
- Exploit idea: Use forked-mainnet state to exercise the firstExcludedIndex boundary path against getAssetCurrentLimit and look for distribution loop breaking value conservation or liveness.
- Invariant to test: unlocking cannot skip, over-unlock, or permanently strand requests; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: measure loops over nodeDelegatorQueue/user queues and assert bounded gas under max configured counts Use probe condition: Swell swETH legacy route; amount case 2 wei; timing exactly at daily reset; caller model EOA caller.
