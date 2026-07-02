# Q2468: getAssetCurrentLimit Highest Price Ratchet Deposit Limit LRTConverter P2468

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and cause highestRsethPrice to ratchet from donated or transient balances then later reverse, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that price protection cannot freeze funds or make withdrawals insolvent from transient TVL; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to permanent freezing of funds? Probe condition: LRTConverter ETH-in-withdrawal route; amount case exact minAmount; timing exactly at daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: cause highestRsethPrice to ratchet from donated or transient balances then later reverse; validation style: compare ETH, stETH, and ETHx branches under the same value; probe condition: LRTConverter ETH-in-withdrawal route; amount case exact minAmount; timing exactly at daily reset; caller model EOA caller
- Exploit idea: Use asset pair differential to exercise the highest-price ratchet path against getAssetCurrentLimit and look for deposit limit breaking value conservation or liveness.
- Invariant to test: price protection cannot freeze funds or make withdrawals insolvent from transient TVL; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: fuzz deposits around getAssetCurrentLimit and assert total deposits never exceed the configured limit by more than intended rounding Use probe condition: LRTConverter ETH-in-withdrawal route; amount case exact minAmount; timing exactly at daily reset; caller model EOA caller.
