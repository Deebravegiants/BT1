# Q713: depositAsset Unexpected Receiver Revert Deposit Limit Merkle-free P0713

## Question
Can an unprivileged LST depositor enter through `external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)` while controlling asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior and use a receiver contract that rejects ETH or token callbacks during completion, causing `contracts/LRTDepositPool.sol::depositAsset` to break the invariant that one receiver cannot freeze protocol-wide funds or consume other users liquidity; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for depositAsset, leading to permanent freezing of funds? Probe condition: Merkle-free yield accounting route; amount case available liquidity minus 1 wei; timing same block after updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositAsset
- Entrypoint: external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)
- Attacker controls: asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior; scenario: use a receiver contract that rejects ETH or token callbacks during completion; validation style: several attacker accounts creating adjacent requests; probe condition: Merkle-free yield accounting route; amount case available liquidity minus 1 wei; timing same block after updateRSETHPrice; caller model EOA caller
- Exploit idea: Use multi-account queue pressure to exercise the unexpected receiver revert path against depositAsset and look for deposit limit breaking value conservation or liveness.
- Invariant to test: one receiver cannot freeze protocol-wide funds or consume other users liquidity; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for depositAsset
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: fuzz deposits around getAssetCurrentLimit and assert total deposits never exceed the configured limit by more than intended rounding Use probe condition: Merkle-free yield accounting route; amount case available liquidity minus 1 wei; timing same block after updateRSETHPrice; caller model EOA caller.
