# Q2619: getAssetCurrentLimit Unbounded Event/data Growth Deposit Limit Lido P2619

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and force huge arrays or strings through accepted inputs that are later used by automation, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that accepted public inputs cannot cause block stuffing or persistent gas grief in settlement; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to permanent freezing of funds? Probe condition: Lido stETH unstake route; amount case 31.999999 ether; timing exactly at daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: force huge arrays or strings through accepted inputs that are later used by automation; validation style: a helper contract batching allowed public calls; probe condition: Lido stETH unstake route; amount case 31.999999 ether; timing exactly at daily reset; caller model EOA caller
- Exploit idea: Use batched multicall-style sequence to exercise the unbounded event/data growth path against getAssetCurrentLimit and look for deposit limit breaking value conservation or liveness.
- Invariant to test: accepted public inputs cannot cause block stuffing or persistent gas grief in settlement; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: fuzz deposits around getAssetCurrentLimit and assert total deposits never exceed the configured limit by more than intended rounding Use probe condition: Lido stETH unstake route; amount case 31.999999 ether; timing exactly at daily reset; caller model EOA caller.
