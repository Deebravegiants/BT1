# Q2603: getAssetCurrentLimit Allowance Race Distribution Loop ETHx P2603

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and change ERC20 allowance/balance between calculation and transfer using supported token behavior, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that protocol mints/burns only after actual spendable value is secured; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to temporary freezing of funds? Probe condition: ETHx supported asset route; amount case 31.999999 ether; timing exactly at daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: change ERC20 allowance/balance between calculation and transfer using supported token behavior; validation style: a local supported-token harness with configurable transfer behavior; probe condition: ETHx supported asset route; amount case 31.999999 ether; timing exactly at daily reset; caller model EOA caller
- Exploit idea: Use malicious ERC20 harness to exercise the allowance race path against getAssetCurrentLimit and look for distribution loop breaking value conservation or liveness.
- Invariant to test: protocol mints/burns only after actual spendable value is secured; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: measure loops over nodeDelegatorQueue/user queues and assert bounded gas under max configured counts Use probe condition: ETHx supported asset route; amount case 31.999999 ether; timing exactly at daily reset; caller model EOA caller.
