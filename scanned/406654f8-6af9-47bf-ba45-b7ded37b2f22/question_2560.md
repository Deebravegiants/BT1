# Q2560: getAssetCurrentLimit Gas Amplified Loop Deposit Limit Swell P2560

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and grow a user-controlled queue/list then trigger a function that iterates it in a critical flow, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that user-controlled growth remains bounded and cannot cause unbounded gas consumption; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to permanent freezing of funds? Probe condition: Swell swETH legacy route; amount case 0.01 ether; timing exactly at daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: grow a user-controlled queue/list then trigger a function that iterates it in a critical flow; validation style: a fork test using current deployed balances and supported assets; probe condition: Swell swETH legacy route; amount case 0.01 ether; timing exactly at daily reset; caller model EOA caller
- Exploit idea: Use forked-mainnet state to exercise the gas-amplified loop path against getAssetCurrentLimit and look for deposit limit breaking value conservation or liveness.
- Invariant to test: user-controlled growth remains bounded and cannot cause unbounded gas consumption; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: fuzz deposits around getAssetCurrentLimit and assert total deposits never exceed the configured limit by more than intended rounding Use probe condition: Swell swETH legacy route; amount case 0.01 ether; timing exactly at daily reset; caller model EOA caller.
