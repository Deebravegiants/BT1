# Q736: depositAsset Committed Assets Desync Rounding queued P0736

## Question
Can an unprivileged LST depositor enter through `external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)` while controlling asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior and create committed withdrawal assets then make total asset accounting move independently, causing `contracts/LRTDepositPool.sol::depositAsset` to break the invariant that assetsCommitted never exceeds realistically available assets in a way that strands users; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for depositAsset, leading to protocol insolvency? Probe condition: queued buffer route; amount case available liquidity exactly; timing same block after updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositAsset
- Entrypoint: external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)
- Attacker controls: asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior; scenario: create committed withdrawal assets then make total asset accounting move independently; validation style: a fork test using current deployed balances and supported assets; probe condition: queued buffer route; amount case available liquidity exactly; timing same block after updateRSETHPrice; caller model EOA caller
- Exploit idea: Use forked-mainnet state to exercise the committed-assets desync path against depositAsset and look for rounding breaking value conservation or liveness.
- Invariant to test: assetsCommitted never exceeds realistically available assets in a way that strands users; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for depositAsset
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: queued buffer route; amount case available liquidity exactly; timing same block after updateRSETHPrice; caller model EOA caller.
