# Q2522: getAssetCurrentLimit Claim Replay Distribution Loop stETH P2522

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and repeat a claim, completion, or callback after state deletion or transfer occurs, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that one claim/request/NFT/token id settles at most once; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to block stuffing? Probe condition: stETH supported asset route; amount case 0.001 ether; timing exactly at daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: repeat a claim, completion, or callback after state deletion or transfer occurs; validation style: two transactions before and after updateRSETHPrice; probe condition: stETH supported asset route; amount case 0.001 ether; timing exactly at daily reset; caller model EOA caller
- Exploit idea: Use two-step sequence to exercise the claim replay path against getAssetCurrentLimit and look for distribution loop breaking value conservation or liveness.
- Invariant to test: one claim/request/NFT/token id settles at most once; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Low. Block stuffing
- Fast validation: measure loops over nodeDelegatorQueue/user queues and assert bounded gas under max configured counts Use probe condition: stETH supported asset route; amount case 0.001 ether; timing exactly at daily reset; caller model EOA caller.
