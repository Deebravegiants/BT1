# Q716: depositAsset Unexpected Receiver Revert Reentrancy queued P0716

## Question
Can an unprivileged LST depositor enter through `external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)` while controlling asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior and use a receiver contract that rejects ETH or token callbacks during completion, causing `contracts/LRTDepositPool.sol::depositAsset` to break the invariant that one receiver cannot freeze protocol-wide funds or consume other users liquidity; specifically, reentrancy must not violate backing, queue, yield, or liquidity accounting for depositAsset, leading to failure to deliver promised returns without principal loss? Probe condition: queued buffer route; amount case available liquidity minus 1 wei; timing same block after updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositAsset
- Entrypoint: external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)
- Attacker controls: asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior; scenario: use a receiver contract that rejects ETH or token callbacks during completion; validation style: compare ETH, stETH, and ETHx branches under the same value; probe condition: queued buffer route; amount case available liquidity minus 1 wei; timing same block after updateRSETHPrice; caller model EOA caller
- Exploit idea: Use asset pair differential to exercise the unexpected receiver revert path against depositAsset and look for reentrancy breaking value conservation or liveness.
- Invariant to test: one receiver cannot freeze protocol-wide funds or consume other users liquidity; specifically, reentrancy must not violate backing, queue, yield, or liquidity accounting for depositAsset
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: use a callback-capable token/receiver harness and assert no second mint, burn, unlock, or transfer succeeds Use probe condition: queued buffer route; amount case available liquidity minus 1 wei; timing same block after updateRSETHPrice; caller model EOA caller.
