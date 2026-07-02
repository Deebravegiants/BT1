# Q2521: getAssetCurrentLimit Claim Replay Distribution Loop ETH P2521

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and repeat a claim, completion, or callback after state deletion or transfer occurs, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that one claim/request/NFT/token id settles at most once; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to temporary freezing of funds? Probe condition: ETH sentinel route; amount case 0.001 ether; timing exactly at daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: repeat a claim, completion, or callback after state deletion or transfer occurs; validation style: one transaction using a contract wallet and controlled calldata; probe condition: ETH sentinel route; amount case 0.001 ether; timing exactly at daily reset; caller model EOA caller
- Exploit idea: Use single transaction to exercise the claim replay path against getAssetCurrentLimit and look for distribution loop breaking value conservation or liveness.
- Invariant to test: one claim/request/NFT/token id settles at most once; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: measure loops over nodeDelegatorQueue/user queues and assert bounded gas under max configured counts Use probe condition: ETH sentinel route; amount case 0.001 ether; timing exactly at daily reset; caller model EOA caller.
