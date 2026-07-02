# Q404: depositAsset Round Down Accumulation Rounding rsETH P0404

## Question
Can an unprivileged LST depositor enter through `external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)` while controlling asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior and split a large action into many dust-sized calls to accumulate rounding residue in the attacker direction, causing `contracts/LRTDepositPool.sol::depositAsset` to break the invariant that sum of split outputs is not greater than one equivalent unsplit output; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for depositAsset, leading to temporary freezing of funds? Probe condition: rsETH burn route; amount case 1 wei; timing same block after updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositAsset
- Entrypoint: external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)
- Attacker controls: asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior; scenario: split a large action into many dust-sized calls to accumulate rounding residue in the attacker direction; validation style: compare ETH, stETH, and ETHx branches under the same value; probe condition: rsETH burn route; amount case 1 wei; timing same block after updateRSETHPrice; caller model EOA caller
- Exploit idea: Use asset pair differential to exercise the round-down accumulation path against depositAsset and look for rounding breaking value conservation or liveness.
- Invariant to test: sum of split outputs is not greater than one equivalent unsplit output; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for depositAsset
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: rsETH burn route; amount case 1 wei; timing same block after updateRSETHPrice; caller model EOA caller.
