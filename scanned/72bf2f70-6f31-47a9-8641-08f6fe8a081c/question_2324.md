# Q2324: getAssetCurrentLimit Round Down Accumulation Deposit Limit rsETH P2324

## Question
Can an unprivileged depositor enter through `depositETH/depositAsset checks getAssetCurrentLimit(asset)` while controlling deposit amount, asset choice, and repeated small deposits and split a large action into many dust-sized calls to accumulate rounding residue in the attacker direction, causing `contracts/LRTDepositPool.sol::getAssetCurrentLimit` to break the invariant that sum of split outputs is not greater than one equivalent unsplit output; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit, leading to permanent freezing of funds? Probe condition: rsETH burn route; amount case available liquidity exactly; timing one second before daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetCurrentLimit
- Entrypoint: depositETH/depositAsset checks getAssetCurrentLimit(asset)
- Attacker controls: deposit amount, asset choice, and repeated small deposits; scenario: split a large action into many dust-sized calls to accumulate rounding residue in the attacker direction; validation style: compare ETH, stETH, and ETHx branches under the same value; probe condition: rsETH burn route; amount case available liquidity exactly; timing one second before daily reset; caller model EOA caller
- Exploit idea: Use asset pair differential to exercise the round-down accumulation path against getAssetCurrentLimit and look for deposit limit breaking value conservation or liveness.
- Invariant to test: sum of split outputs is not greater than one equivalent unsplit output; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for getAssetCurrentLimit
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: fuzz deposits around getAssetCurrentLimit and assert total deposits never exceed the configured limit by more than intended rounding Use probe condition: rsETH burn route; amount case available liquidity exactly; timing one second before daily reset; caller model EOA caller.
