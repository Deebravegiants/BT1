# Q2601: getAssetCurrentLimit Allowance Race Deposit Limit ETH P2601

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and change ERC20 allowance/balance between calculation and transfer using supported token behavior, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that protocol mints/burns only after actual spendable value is secured; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to permanent freezing of funds? Probe condition: ETH sentinel route; amount case 31.999999 ether; timing exactly at daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: change ERC20 allowance/balance between calculation and transfer using supported token behavior; validation style: warp/block-roll around day or withdrawal-delay boundaries; probe condition: ETH sentinel route; amount case 31.999999 ether; timing exactly at daily reset; caller model EOA caller
- Exploit idea: Use period boundary fuzz to exercise the allowance race path against getAssetCurrentLimit and look for deposit limit breaking value conservation or liveness.
- Invariant to test: protocol mints/burns only after actual spendable value is secured; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: fuzz deposits around getAssetCurrentLimit and assert total deposits never exceed the configured limit by more than intended rounding Use probe condition: ETH sentinel route; amount case 31.999999 ether; timing exactly at daily reset; caller model EOA caller.
