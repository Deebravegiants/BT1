# Q2571: getAssetCurrentLimit Asset Identity Confusion Deposit Limit EigenLayer P2571

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and use ETH sentinel, WETH, stETH, ETHx, or unsupported token addresses at branch boundaries, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that ETH and ERC20 branches cannot be confused to transfer or account the wrong asset; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to permanent freezing of funds? Probe condition: EigenLayer queued-withdrawal route; amount case 0.1 ether; timing exactly at daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: use ETH sentinel, WETH, stETH, ETHx, or unsupported token addresses at branch boundaries; validation style: a helper contract batching allowed public calls; probe condition: EigenLayer queued-withdrawal route; amount case 0.1 ether; timing exactly at daily reset; caller model EOA caller
- Exploit idea: Use batched multicall-style sequence to exercise the asset identity confusion path against getAssetCurrentLimit and look for deposit limit breaking value conservation or liveness.
- Invariant to test: ETH and ERC20 branches cannot be confused to transfer or account the wrong asset; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: fuzz deposits around getAssetCurrentLimit and assert total deposits never exceed the configured limit by more than intended rounding Use probe condition: EigenLayer queued-withdrawal route; amount case 0.1 ether; timing exactly at daily reset; caller model EOA caller.
