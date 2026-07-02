# Q487: depositAsset Pause Boundary Race Rounding FeeReceiver P0487

## Question
Can an unprivileged LST depositor enter through `external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)` while controlling asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior and race a public action around a pause or public price-triggered pause transition, causing `contracts/LRTDepositPool.sol::depositAsset` to break the invariant that paused state cannot leave assets burned, committed, or transferred without corresponding settlement; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for depositAsset, leading to failure to deliver promised returns without principal loss? Probe condition: FeeReceiver reward route; amount case minAmount plus 1 wei; timing same block after updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositAsset
- Entrypoint: external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)
- Attacker controls: asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior; scenario: race a public action around a pause or public price-triggered pause transition; validation style: an attacker contract as msg.sender or recipient; probe condition: FeeReceiver reward route; amount case minAmount plus 1 wei; timing same block after updateRSETHPrice; caller model EOA caller
- Exploit idea: Use receiver contract path to exercise the pause boundary race path against depositAsset and look for rounding breaking value conservation or liveness.
- Invariant to test: paused state cannot leave assets burned, committed, or transferred without corresponding settlement; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for depositAsset
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: FeeReceiver reward route; amount case minAmount plus 1 wei; timing same block after updateRSETHPrice; caller model EOA caller.
