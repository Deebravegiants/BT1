# Q2347: getAssetCurrentLimit Zero Or Dust Edge Rounding FeeReceiver P2347

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and use zero-like, one-wei, or min-threshold-adjacent amounts to bypass accounting updates, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that dust inputs cannot create withdrawable value or stuck committed assets; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to protocol insolvency? Probe condition: FeeReceiver reward route; amount case available liquidity plus 1 wei; timing one second before daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: use zero-like, one-wei, or min-threshold-adjacent amounts to bypass accounting updates; validation style: an attacker contract as msg.sender or recipient; probe condition: FeeReceiver reward route; amount case available liquidity plus 1 wei; timing one second before daily reset; caller model EOA caller
- Exploit idea: Use receiver contract path to exercise the zero-or-dust edge path against getAssetCurrentLimit and look for rounding breaking value conservation or liveness.
- Invariant to test: dust inputs cannot create withdrawable value or stuck committed assets; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: FeeReceiver reward route; amount case available liquidity plus 1 wei; timing one second before daily reset; caller model EOA caller.
