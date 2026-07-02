# Q737: depositAsset Committed Assets Desync Fee On Transfer daily P0737

## Question
Can an unprivileged LST depositor enter through `external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)` while controlling asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior and create committed withdrawal assets then make total asset accounting move independently, causing `contracts/LRTDepositPool.sol::depositAsset` to break the invariant that assetsCommitted never exceeds realistically available assets in a way that strands users; specifically, fee on transfer must not violate backing, queue, yield, or liquidity accounting for depositAsset, leading to temporary freezing of funds? Probe condition: daily mint limit route; amount case available liquidity exactly; timing same block after updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositAsset
- Entrypoint: external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)
- Attacker controls: asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior; scenario: create committed withdrawal assets then make total asset accounting move independently; validation style: several attacker accounts creating adjacent requests; probe condition: daily mint limit route; amount case available liquidity exactly; timing same block after updateRSETHPrice; caller model EOA caller
- Exploit idea: Use multi-account queue pressure to exercise the committed-assets desync path against depositAsset and look for fee on transfer breaking value conservation or liveness.
- Invariant to test: assetsCommitted never exceeds realistically available assets in a way that strands users; specifically, fee on transfer must not violate backing, queue, yield, or liquidity accounting for depositAsset
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: support a local fee-on-transfer token in a fork harness and assert actual received amount is used Use probe condition: daily mint limit route; amount case available liquidity exactly; timing same block after updateRSETHPrice; caller model EOA caller.
