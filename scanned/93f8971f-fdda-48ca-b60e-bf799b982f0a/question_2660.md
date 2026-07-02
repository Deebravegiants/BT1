# Q2660: getAssetCurrentLimit Committed Assets Desync Deposit Limit Swell P2660

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and create committed withdrawal assets then make total asset accounting move independently, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that assetsCommitted never exceeds realistically available assets in a way that strands users; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to permanent freezing of funds? Probe condition: Swell swETH legacy route; amount case 32.000001 ether; timing exactly at daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: create committed withdrawal assets then make total asset accounting move independently; validation style: compare ETH, stETH, and ETHx branches under the same value; probe condition: Swell swETH legacy route; amount case 32.000001 ether; timing exactly at daily reset; caller model EOA caller
- Exploit idea: Use asset pair differential to exercise the committed-assets desync path against getAssetCurrentLimit and look for deposit limit breaking value conservation or liveness.
- Invariant to test: assetsCommitted never exceeds realistically available assets in a way that strands users; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: fuzz deposits around getAssetCurrentLimit and assert total deposits never exceed the configured limit by more than intended rounding Use probe condition: Swell swETH legacy route; amount case 32.000001 ether; timing exactly at daily reset; caller model EOA caller.
