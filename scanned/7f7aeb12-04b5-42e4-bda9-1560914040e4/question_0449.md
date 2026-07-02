# Q449: depositAsset Fee On Transfer Token Skew Fee On Transfer LRTUnstakingVault P0449

## Question
Can an unprivileged LST depositor enter through `external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)` while controlling asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior and use a supported ERC20 path where received balance is lower than depositAmount or transfer amount, causing `contracts/LRTDepositPool.sol::depositAsset` to break the invariant that minted rsETH and committed withdrawals are based on actual assets received; specifically, fee on transfer must not violate backing, queue, yield, or liquidity accounting for depositAsset, leading to failure to deliver promised returns without principal loss? Probe condition: LRTUnstakingVault instant-liquidity route; amount case minAmount minus 1 wei; timing same block after updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositAsset
- Entrypoint: external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)
- Attacker controls: asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior; scenario: use a supported ERC20 path where received balance is lower than depositAmount or transfer amount; validation style: several attacker accounts creating adjacent requests; probe condition: LRTUnstakingVault instant-liquidity route; amount case minAmount minus 1 wei; timing same block after updateRSETHPrice; caller model EOA caller
- Exploit idea: Use multi-account queue pressure to exercise the fee-on-transfer token skew path against depositAsset and look for fee on transfer breaking value conservation or liveness.
- Invariant to test: minted rsETH and committed withdrawals are based on actual assets received; specifically, fee on transfer must not violate backing, queue, yield, or liquidity accounting for depositAsset
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: support a local fee-on-transfer token in a fork harness and assert actual received amount is used Use probe condition: LRTUnstakingVault instant-liquidity route; amount case minAmount minus 1 wei; timing same block after updateRSETHPrice; caller model EOA caller.
