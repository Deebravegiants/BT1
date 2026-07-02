# Q687: depositAsset Cross Contract Stale Read Fee On Transfer FeeReceiver P0687

## Question
Can an unprivileged LST depositor enter through `external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)` while controlling asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior and make one contract read another contract before its state reflects a prior step in the same attack sequence, causing `contracts/LRTDepositPool.sol::depositAsset` to break the invariant that cross-contract accounting snapshots cannot be inconsistent enough to steal or freeze funds; specifically, fee on transfer must not violate backing, queue, yield, or liquidity accounting for depositAsset, leading to protocol insolvency? Probe condition: FeeReceiver reward route; amount case daily limit exactly; timing same block after updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositAsset
- Entrypoint: external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)
- Attacker controls: asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior; scenario: make one contract read another contract before its state reflects a prior step in the same attack sequence; validation style: a helper contract batching allowed public calls; probe condition: FeeReceiver reward route; amount case daily limit exactly; timing same block after updateRSETHPrice; caller model EOA caller
- Exploit idea: Use batched multicall-style sequence to exercise the cross-contract stale read path against depositAsset and look for fee on transfer breaking value conservation or liveness.
- Invariant to test: cross-contract accounting snapshots cannot be inconsistent enough to steal or freeze funds; specifically, fee on transfer must not violate backing, queue, yield, or liquidity accounting for depositAsset
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: support a local fee-on-transfer token in a fork harness and assert actual received amount is used Use probe condition: FeeReceiver reward route; amount case daily limit exactly; timing same block after updateRSETHPrice; caller model EOA caller.
