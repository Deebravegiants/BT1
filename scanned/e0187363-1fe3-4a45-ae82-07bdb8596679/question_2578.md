# Q2578: getAssetCurrentLimit Asset Identity Confusion Distribution Loop daily P2578

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and use ETH sentinel, WETH, stETH, ETHx, or unsupported token addresses at branch boundaries, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that ETH and ERC20 branches cannot be confused to transfer or account the wrong asset; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to block stuffing? Probe condition: daily fee mint limit route; amount case 0.1 ether; timing exactly at daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: use ETH sentinel, WETH, stETH, ETHx, or unsupported token addresses at branch boundaries; validation style: stateful fuzzing over deposit, update price, withdraw, unlock, complete; probe condition: daily fee mint limit route; amount case 0.1 ether; timing exactly at daily reset; caller model EOA caller
- Exploit idea: Use stateful invariant fuzz to exercise the asset identity confusion path against getAssetCurrentLimit and look for distribution loop breaking value conservation or liveness.
- Invariant to test: ETH and ERC20 branches cannot be confused to transfer or account the wrong asset; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Low. Block stuffing
- Fast validation: measure loops over nodeDelegatorQueue/user queues and assert bounded gas under max configured counts Use probe condition: daily fee mint limit route; amount case 0.1 ether; timing exactly at daily reset; caller model EOA caller.
