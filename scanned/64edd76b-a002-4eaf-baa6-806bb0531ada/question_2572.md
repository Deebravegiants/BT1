# Q2572: getAssetCurrentLimit Asset Identity Confusion Rounding Aave P2572

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and use ETH sentinel, WETH, stETH, ETHx, or unsupported token addresses at branch boundaries, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that ETH and ERC20 branches cannot be confused to transfer or account the wrong asset; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to protocol insolvency? Probe condition: Aave aWETH liquidity route; amount case 0.1 ether; timing exactly at daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: use ETH sentinel, WETH, stETH, ETHx, or unsupported token addresses at branch boundaries; validation style: a fork test using current deployed balances and supported assets; probe condition: Aave aWETH liquidity route; amount case 0.1 ether; timing exactly at daily reset; caller model EOA caller
- Exploit idea: Use forked-mainnet state to exercise the asset identity confusion path against getAssetCurrentLimit and look for rounding breaking value conservation or liveness.
- Invariant to test: ETH and ERC20 branches cannot be confused to transfer or account the wrong asset; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: Aave aWETH liquidity route; amount case 0.1 ether; timing exactly at daily reset; caller model EOA caller.
