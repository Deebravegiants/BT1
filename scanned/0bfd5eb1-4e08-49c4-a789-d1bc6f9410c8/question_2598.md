# Q2598: getAssetCurrentLimit Allowance Race Rounding daily P2598

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and change ERC20 allowance/balance between calculation and transfer using supported token behavior, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that protocol mints/burns only after actual spendable value is secured; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to protocol insolvency? Probe condition: daily fee mint limit route; amount case 1 ether; timing exactly at daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: change ERC20 allowance/balance between calculation and transfer using supported token behavior; validation style: compare many dust calls against one large call; probe condition: daily fee mint limit route; amount case 1 ether; timing exactly at daily reset; caller model EOA caller
- Exploit idea: Use dust-to-large differential to exercise the allowance race path against getAssetCurrentLimit and look for rounding breaking value conservation or liveness.
- Invariant to test: protocol mints/burns only after actual spendable value is secured; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: daily fee mint limit route; amount case 1 ether; timing exactly at daily reset; caller model EOA caller.
