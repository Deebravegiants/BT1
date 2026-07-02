# Q405: depositAsset Round Down Accumulation Fee On Transfer rsETH P0405

## Question
Can an unprivileged LST depositor enter through `external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)` while controlling asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior and split a large action into many dust-sized calls to accumulate rounding residue in the attacker direction, causing `contracts/LRTDepositPool.sol::depositAsset` to break the invariant that sum of split outputs is not greater than one equivalent unsplit output; specifically, fee on transfer must not violate backing, queue, yield, or liquidity accounting for depositAsset, leading to failure to deliver promised returns without principal loss? Probe condition: rsETH transfer route; amount case 1 wei; timing same block after updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositAsset
- Entrypoint: external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)
- Attacker controls: asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior; scenario: split a large action into many dust-sized calls to accumulate rounding residue in the attacker direction; validation style: warp/block-roll around day or withdrawal-delay boundaries; probe condition: rsETH transfer route; amount case 1 wei; timing same block after updateRSETHPrice; caller model EOA caller
- Exploit idea: Use period boundary fuzz to exercise the round-down accumulation path against depositAsset and look for fee on transfer breaking value conservation or liveness.
- Invariant to test: sum of split outputs is not greater than one equivalent unsplit output; specifically, fee on transfer must not violate backing, queue, yield, or liquidity accounting for depositAsset
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: support a local fee-on-transfer token in a fork harness and assert actual received amount is used Use probe condition: rsETH transfer route; amount case 1 wei; timing same block after updateRSETHPrice; caller model EOA caller.
