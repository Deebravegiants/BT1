# Q2434: getAssetCurrentLimit Nonce Collision Attempt Distribution Loop deposit-limit P2434

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and create requests across assets/accounts so nonce-derived ids collide or are consumed out of order, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that request ids remain unique per asset and cannot release another user request; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to block stuffing? Probe condition: deposit-limit accounting route; amount case 2 wei; timing exactly at daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: create requests across assets/accounts so nonce-derived ids collide or are consumed out of order; validation style: stateful fuzzing over deposit, update price, withdraw, unlock, complete; probe condition: deposit-limit accounting route; amount case 2 wei; timing exactly at daily reset; caller model EOA caller
- Exploit idea: Use stateful invariant fuzz to exercise the nonce collision attempt path against getAssetCurrentLimit and look for distribution loop breaking value conservation or liveness.
- Invariant to test: request ids remain unique per asset and cannot release another user request; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Low. Block stuffing
- Fast validation: measure loops over nodeDelegatorQueue/user queues and assert bounded gas under max configured counts Use probe condition: deposit-limit accounting route; amount case 2 wei; timing exactly at daily reset; caller model EOA caller.
