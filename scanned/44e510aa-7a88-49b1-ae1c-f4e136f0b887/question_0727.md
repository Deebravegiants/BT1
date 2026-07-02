# Q727: depositAsset Supply Zero Transition Reentrancy FeeReceiver P0727

## Question
Can an unprivileged LST depositor enter through `external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)` while controlling asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior and operate around the transition from zero rsETH supply to nonzero supply or back toward zero, causing `contracts/LRTDepositPool.sol::depositAsset` to break the invariant that initial price and final withdrawals cannot create unbacked supply or insolvency; specifically, reentrancy must not violate backing, queue, yield, or liquidity accounting for depositAsset, leading to failure to deliver promised returns without principal loss? Probe condition: FeeReceiver reward route; amount case available liquidity exactly; timing same block after updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositAsset
- Entrypoint: external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)
- Attacker controls: asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior; scenario: operate around the transition from zero rsETH supply to nonzero supply or back toward zero; validation style: an attacker contract as msg.sender or recipient; probe condition: FeeReceiver reward route; amount case available liquidity exactly; timing same block after updateRSETHPrice; caller model EOA caller
- Exploit idea: Use receiver contract path to exercise the supply-zero transition path against depositAsset and look for reentrancy breaking value conservation or liveness.
- Invariant to test: initial price and final withdrawals cannot create unbacked supply or insolvency; specifically, reentrancy must not violate backing, queue, yield, or liquidity accounting for depositAsset
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: use a callback-capable token/receiver harness and assert no second mint, burn, unlock, or transfer succeeds Use probe condition: FeeReceiver reward route; amount case available liquidity exactly; timing same block after updateRSETHPrice; caller model EOA caller.
