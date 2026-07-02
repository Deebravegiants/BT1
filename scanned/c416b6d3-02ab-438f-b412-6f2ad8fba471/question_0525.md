# Q525: depositAsset FirstExcludedIndex Boundary Deposit Limit rsETH P0525

## Question
Can an unprivileged LST depositor enter through `external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)` while controlling asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior and fill withdrawal requests around the unlockQueue firstExcludedIndex boundary, causing `contracts/LRTDepositPool.sol::depositAsset` to break the invariant that unlocking cannot skip, over-unlock, or permanently strand requests; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for depositAsset, leading to failure to deliver promised returns without principal loss? Probe condition: rsETH transfer route; amount case 0.001 ether; timing same block after updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositAsset
- Entrypoint: external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)
- Attacker controls: asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior; scenario: fill withdrawal requests around the unlockQueue firstExcludedIndex boundary; validation style: warp/block-roll around day or withdrawal-delay boundaries; probe condition: rsETH transfer route; amount case 0.001 ether; timing same block after updateRSETHPrice; caller model EOA caller
- Exploit idea: Use period boundary fuzz to exercise the firstExcludedIndex boundary path against depositAsset and look for deposit limit breaking value conservation or liveness.
- Invariant to test: unlocking cannot skip, over-unlock, or permanently strand requests; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for depositAsset
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: fuzz deposits around getAssetCurrentLimit and assert total deposits never exceed the configured limit by more than intended rounding Use probe condition: rsETH transfer route; amount case 0.001 ether; timing same block after updateRSETHPrice; caller model EOA caller.
