# Q2600: getAssetCurrentLimit Allowance Race Distribution Loop Swell P2600

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and change ERC20 allowance/balance between calculation and transfer using supported token behavior, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that protocol mints/burns only after actual spendable value is secured; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to block stuffing? Probe condition: Swell swETH legacy route; amount case 1 ether; timing exactly at daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: change ERC20 allowance/balance between calculation and transfer using supported token behavior; validation style: compare ETH, stETH, and ETHx branches under the same value; probe condition: Swell swETH legacy route; amount case 1 ether; timing exactly at daily reset; caller model EOA caller
- Exploit idea: Use asset pair differential to exercise the allowance race path against getAssetCurrentLimit and look for distribution loop breaking value conservation or liveness.
- Invariant to test: protocol mints/burns only after actual spendable value is secured; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Low. Block stuffing
- Fast validation: measure loops over nodeDelegatorQueue/user queues and assert bounded gas under max configured counts Use probe condition: Swell swETH legacy route; amount case 1 ether; timing exactly at daily reset; caller model EOA caller.
