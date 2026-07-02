# Q726: depositAsset Supply Zero Transition Fee On Transfer LRTOracle P0726

## Question
Can an unprivileged LST depositor enter through `external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)` while controlling asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior and operate around the transition from zero rsETH supply to nonzero supply or back toward zero, causing `contracts/LRTDepositPool.sol::depositAsset` to break the invariant that initial price and final withdrawals cannot create unbacked supply or insolvency; specifically, fee on transfer must not violate backing, queue, yield, or liquidity accounting for depositAsset, leading to temporary freezing of funds? Probe condition: LRTOracle price route; amount case available liquidity exactly; timing same block after updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositAsset
- Entrypoint: external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)
- Attacker controls: asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior; scenario: operate around the transition from zero rsETH supply to nonzero supply or back toward zero; validation style: compare many dust calls against one large call; probe condition: LRTOracle price route; amount case available liquidity exactly; timing same block after updateRSETHPrice; caller model EOA caller
- Exploit idea: Use dust-to-large differential to exercise the supply-zero transition path against depositAsset and look for fee on transfer breaking value conservation or liveness.
- Invariant to test: initial price and final withdrawals cannot create unbacked supply or insolvency; specifically, fee on transfer must not violate backing, queue, yield, or liquidity accounting for depositAsset
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: support a local fee-on-transfer token in a fork harness and assert actual received amount is used Use probe condition: LRTOracle price route; amount case available liquidity exactly; timing same block after updateRSETHPrice; caller model EOA caller.
