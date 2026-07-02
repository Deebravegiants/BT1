# Q2436: getAssetCurrentLimit Nonce Collision Attempt Rounding queued P2436

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and create requests across assets/accounts so nonce-derived ids collide or are consumed out of order, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that request ids remain unique per asset and cannot release another user request; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to protocol insolvency? Probe condition: queued buffer route; amount case 2 wei; timing exactly at daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: create requests across assets/accounts so nonce-derived ids collide or are consumed out of order; validation style: attacker-created state followed by an honest operator action; probe condition: queued buffer route; amount case 2 wei; timing exactly at daily reset; caller model EOA caller
- Exploit idea: Use operator-normalization follow-up to exercise the nonce collision attempt path against getAssetCurrentLimit and look for rounding breaking value conservation or liveness.
- Invariant to test: request ids remain unique per asset and cannot release another user request; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: queued buffer route; amount case 2 wei; timing exactly at daily reset; caller model EOA caller.
