# Q2469: getAssetCurrentLimit Highest Price Ratchet Rounding LRTUnstakingVault P2469

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and cause highestRsethPrice to ratchet from donated or transient balances then later reverse, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that price protection cannot freeze funds or make withdrawals insolvent from transient TVL; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to protocol insolvency? Probe condition: LRTUnstakingVault instant-liquidity route; amount case exact minAmount; timing exactly at daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: cause highestRsethPrice to ratchet from donated or transient balances then later reverse; validation style: warp/block-roll around day or withdrawal-delay boundaries; probe condition: LRTUnstakingVault instant-liquidity route; amount case exact minAmount; timing exactly at daily reset; caller model EOA caller
- Exploit idea: Use period boundary fuzz to exercise the highest-price ratchet path against getAssetCurrentLimit and look for rounding breaking value conservation or liveness.
- Invariant to test: price protection cannot freeze funds or make withdrawals insolvent from transient TVL; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: LRTUnstakingVault instant-liquidity route; amount case exact minAmount; timing exactly at daily reset; caller model EOA caller.
