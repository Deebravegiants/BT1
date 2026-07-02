# Q2516: getAssetCurrentLimit Buffer Over Reservation Deposit Limit queued P2516

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and create queued withdrawal state that makes buffer reserve more than actual liabilities, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that stale buffers cannot permanently freeze free liquidity; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to permanent freezing of funds? Probe condition: queued buffer route; amount case 1 gwei; timing exactly at daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: create queued withdrawal state that makes buffer reserve more than actual liabilities; validation style: compare ETH, stETH, and ETHx branches under the same value; probe condition: queued buffer route; amount case 1 gwei; timing exactly at daily reset; caller model EOA caller
- Exploit idea: Use asset pair differential to exercise the buffer over-reservation path against getAssetCurrentLimit and look for deposit limit breaking value conservation or liveness.
- Invariant to test: stale buffers cannot permanently freeze free liquidity; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: fuzz deposits around getAssetCurrentLimit and assert total deposits never exceed the configured limit by more than intended rounding Use probe condition: queued buffer route; amount case 1 gwei; timing exactly at daily reset; caller model EOA caller.
