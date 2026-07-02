# Q558: depositAsset Fee Mint Limit Boundary Deposit Limit daily P0558

## Question
Can an unprivileged LST depositor enter through `external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)` while controlling asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior and execute price updates at exactly fee-period or mint-period boundaries, causing `contracts/LRTDepositPool.sol::depositAsset` to break the invariant that daily limits cannot be bypassed or permanently block legitimate minting; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for depositAsset, leading to failure to deliver promised returns without principal loss? Probe condition: daily fee mint limit route; amount case 0.01 ether; timing same block after updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositAsset
- Entrypoint: external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)
- Attacker controls: asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior; scenario: execute price updates at exactly fee-period or mint-period boundaries; validation style: compare many dust calls against one large call; probe condition: daily fee mint limit route; amount case 0.01 ether; timing same block after updateRSETHPrice; caller model EOA caller
- Exploit idea: Use dust-to-large differential to exercise the fee mint limit boundary path against depositAsset and look for deposit limit breaking value conservation or liveness.
- Invariant to test: daily limits cannot be bypassed or permanently block legitimate minting; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for depositAsset
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: fuzz deposits around getAssetCurrentLimit and assert total deposits never exceed the configured limit by more than intended rounding Use probe condition: daily fee mint limit route; amount case 0.01 ether; timing same block after updateRSETHPrice; caller model EOA caller.
