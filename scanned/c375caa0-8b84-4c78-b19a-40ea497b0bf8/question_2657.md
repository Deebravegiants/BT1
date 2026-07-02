# Q2657: getAssetCurrentLimit Committed Assets Desync Rounding daily P2657

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and create committed withdrawal assets then make total asset accounting move independently, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that assetsCommitted never exceeds realistically available assets in a way that strands users; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to protocol insolvency? Probe condition: daily mint limit route; amount case 32.000001 ether; timing exactly at daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: create committed withdrawal assets then make total asset accounting move independently; validation style: several attacker accounts creating adjacent requests; probe condition: daily mint limit route; amount case 32.000001 ether; timing exactly at daily reset; caller model EOA caller
- Exploit idea: Use multi-account queue pressure to exercise the committed-assets desync path against getAssetCurrentLimit and look for rounding breaking value conservation or liveness.
- Invariant to test: assetsCommitted never exceeds realistically available assets in a way that strands users; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: daily mint limit route; amount case 32.000001 ether; timing exactly at daily reset; caller model EOA caller.
