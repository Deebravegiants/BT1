# Q2628: getAssetCurrentLimit Unbounded Event/data Growth Rounding LRTConverter P2628

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and force huge arrays or strings through accepted inputs that are later used by automation, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that accepted public inputs cannot cause block stuffing or persistent gas grief in settlement; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to protocol insolvency? Probe condition: LRTConverter ETH-in-withdrawal route; amount case 32 ether; timing exactly at daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: force huge arrays or strings through accepted inputs that are later used by automation; validation style: attacker-created state followed by an honest operator action; probe condition: LRTConverter ETH-in-withdrawal route; amount case 32 ether; timing exactly at daily reset; caller model EOA caller
- Exploit idea: Use operator-normalization follow-up to exercise the unbounded event/data growth path against getAssetCurrentLimit and look for rounding breaking value conservation or liveness.
- Invariant to test: accepted public inputs cannot cause block stuffing or persistent gas grief in settlement; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: LRTConverter ETH-in-withdrawal route; amount case 32 ether; timing exactly at daily reset; caller model EOA caller.
