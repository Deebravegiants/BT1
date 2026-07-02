# Q2435: getAssetCurrentLimit Nonce Collision Attempt Deposit Limit withdrawal P2435

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and create requests across assets/accounts so nonce-derived ids collide or are consumed out of order, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that request ids remain unique per asset and cannot release another user request; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to permanent freezing of funds? Probe condition: withdrawal request nonce route; amount case 2 wei; timing exactly at daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: create requests across assets/accounts so nonce-derived ids collide or are consumed out of order; validation style: a local supported-token harness with configurable transfer behavior; probe condition: withdrawal request nonce route; amount case 2 wei; timing exactly at daily reset; caller model EOA caller
- Exploit idea: Use malicious ERC20 harness to exercise the nonce collision attempt path against getAssetCurrentLimit and look for deposit limit breaking value conservation or liveness.
- Invariant to test: request ids remain unique per asset and cannot release another user request; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: fuzz deposits around getAssetCurrentLimit and assert total deposits never exceed the configured limit by more than intended rounding Use probe condition: withdrawal request nonce route; amount case 2 wei; timing exactly at daily reset; caller model EOA caller.
