# Q422: depositAsset Zero Or Dust Edge Reentrancy stETH P0422

## Question
Can an unprivileged LST depositor enter through `external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)` while controlling asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior and use zero-like, one-wei, or min-threshold-adjacent amounts to bypass accounting updates, causing `contracts/LRTDepositPool.sol::depositAsset` to break the invariant that dust inputs cannot create withdrawable value or stuck committed assets; specifically, reentrancy must not violate backing, queue, yield, or liquidity accounting for depositAsset, leading to failure to deliver promised returns without principal loss? Probe condition: stETH supported asset route; amount case 2 wei; timing same block after updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositAsset
- Entrypoint: external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)
- Attacker controls: asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior; scenario: use zero-like, one-wei, or min-threshold-adjacent amounts to bypass accounting updates; validation style: two transactions before and after updateRSETHPrice; probe condition: stETH supported asset route; amount case 2 wei; timing same block after updateRSETHPrice; caller model EOA caller
- Exploit idea: Use two-step sequence to exercise the zero-or-dust edge path against depositAsset and look for reentrancy breaking value conservation or liveness.
- Invariant to test: dust inputs cannot create withdrawable value or stuck committed assets; specifically, reentrancy must not violate backing, queue, yield, or liquidity accounting for depositAsset
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: use a callback-capable token/receiver harness and assert no second mint, burn, unlock, or transfer succeeds Use probe condition: stETH supported asset route; amount case 2 wei; timing same block after updateRSETHPrice; caller model EOA caller.
