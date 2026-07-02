# Q2479: getAssetCurrentLimit Fee Mint Limit Boundary Deposit Limit Lido P2479

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and execute price updates at exactly fee-period or mint-period boundaries, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that daily limits cannot be bypassed or permanently block legitimate minting; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to permanent freezing of funds? Probe condition: Lido stETH unstake route; amount case exact minAmount; timing exactly at daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: execute price updates at exactly fee-period or mint-period boundaries; validation style: an attacker contract as msg.sender or recipient; probe condition: Lido stETH unstake route; amount case exact minAmount; timing exactly at daily reset; caller model EOA caller
- Exploit idea: Use receiver contract path to exercise the fee mint limit boundary path against getAssetCurrentLimit and look for deposit limit breaking value conservation or liveness.
- Invariant to test: daily limits cannot be bypassed or permanently block legitimate minting; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: fuzz deposits around getAssetCurrentLimit and assert total deposits never exceed the configured limit by more than intended rounding Use probe condition: Lido stETH unstake route; amount case exact minAmount; timing exactly at daily reset; caller model EOA caller.
