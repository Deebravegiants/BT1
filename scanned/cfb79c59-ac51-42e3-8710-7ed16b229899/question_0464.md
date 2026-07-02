# Q464: depositAsset Rebasing Balance Drift Deposit Limit rsETH P0464

## Question
Can an unprivileged LST depositor enter through `external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)` while controlling asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior and let a supported rebasing LST balance change between request creation and final settlement, causing `contracts/LRTDepositPool.sol::depositAsset` to break the invariant that rebases cannot create unbacked rsETH or freeze queued withdrawals; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for depositAsset, leading to temporary freezing of funds? Probe condition: rsETH burn route; amount case exact minAmount; timing same block after updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositAsset
- Entrypoint: external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)
- Attacker controls: asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior; scenario: let a supported rebasing LST balance change between request creation and final settlement; validation style: compare ETH, stETH, and ETHx branches under the same value; probe condition: rsETH burn route; amount case exact minAmount; timing same block after updateRSETHPrice; caller model EOA caller
- Exploit idea: Use asset pair differential to exercise the rebasing balance drift path against depositAsset and look for deposit limit breaking value conservation or liveness.
- Invariant to test: rebases cannot create unbacked rsETH or freeze queued withdrawals; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for depositAsset
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: fuzz deposits around getAssetCurrentLimit and assert total deposits never exceed the configured limit by more than intended rounding Use probe condition: rsETH burn route; amount case exact minAmount; timing same block after updateRSETHPrice; caller model EOA caller.
