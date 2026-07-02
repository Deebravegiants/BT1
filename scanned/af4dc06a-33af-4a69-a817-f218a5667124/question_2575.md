# Q2575: getAssetCurrentLimit Asset Identity Confusion Deposit Limit withdrawal P2575

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and use ETH sentinel, WETH, stETH, ETHx, or unsupported token addresses at branch boundaries, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that ETH and ERC20 branches cannot be confused to transfer or account the wrong asset; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to permanent freezing of funds? Probe condition: withdrawal request nonce route; amount case 0.1 ether; timing exactly at daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: use ETH sentinel, WETH, stETH, ETHx, or unsupported token addresses at branch boundaries; validation style: an attacker contract as msg.sender or recipient; probe condition: withdrawal request nonce route; amount case 0.1 ether; timing exactly at daily reset; caller model EOA caller
- Exploit idea: Use receiver contract path to exercise the asset identity confusion path against getAssetCurrentLimit and look for deposit limit breaking value conservation or liveness.
- Invariant to test: ETH and ERC20 branches cannot be confused to transfer or account the wrong asset; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: fuzz deposits around getAssetCurrentLimit and assert total deposits never exceed the configured limit by more than intended rounding Use probe condition: withdrawal request nonce route; amount case 0.1 ether; timing exactly at daily reset; caller model EOA caller.
