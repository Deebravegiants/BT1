# Q2429: getAssetCurrentLimit Nonce Collision Attempt Distribution Loop LRTUnstakingVault P2429

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and create requests across assets/accounts so nonce-derived ids collide or are consumed out of order, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that request ids remain unique per asset and cannot release another user request; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to temporary freezing of funds? Probe condition: LRTUnstakingVault instant-liquidity route; amount case 2 wei; timing exactly at daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: create requests across assets/accounts so nonce-derived ids collide or are consumed out of order; validation style: several attacker accounts creating adjacent requests; probe condition: LRTUnstakingVault instant-liquidity route; amount case 2 wei; timing exactly at daily reset; caller model EOA caller
- Exploit idea: Use multi-account queue pressure to exercise the nonce collision attempt path against getAssetCurrentLimit and look for distribution loop breaking value conservation or liveness.
- Invariant to test: request ids remain unique per asset and cannot release another user request; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: measure loops over nodeDelegatorQueue/user queues and assert bounded gas under max configured counts Use probe condition: LRTUnstakingVault instant-liquidity route; amount case 2 wei; timing exactly at daily reset; caller model EOA caller.
