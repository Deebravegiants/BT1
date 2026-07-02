# Q670: depositAsset Min Amount Bypass Rounding NodeDelegator P0670

## Question
Can an unprivileged LST depositor enter through `external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)` while controlling asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior and set minRSETHAmountExpected or min expected asset values at boundary values while prices move, causing `contracts/LRTDepositPool.sol::depositAsset` to break the invariant that slippage guards protect users and cannot be weaponized into insolvency; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for depositAsset, leading to protocol insolvency? Probe condition: NodeDelegator pod-share route; amount case daily limit minus 1 wei; timing same block after updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositAsset
- Entrypoint: external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)
- Attacker controls: asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior; scenario: set minRSETHAmountExpected or min expected asset values at boundary values while prices move; validation style: stateful fuzzing over deposit, update price, withdraw, unlock, complete; probe condition: NodeDelegator pod-share route; amount case daily limit minus 1 wei; timing same block after updateRSETHPrice; caller model EOA caller
- Exploit idea: Use stateful invariant fuzz to exercise the min-amount bypass path against depositAsset and look for rounding breaking value conservation or liveness.
- Invariant to test: slippage guards protect users and cannot be weaponized into insolvency; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for depositAsset
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: NodeDelegator pod-share route; amount case daily limit minus 1 wei; timing same block after updateRSETHPrice; caller model EOA caller.
