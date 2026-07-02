# Q436: depositAsset Direct ETH Donation Skew Deposit Limit queued P0436

## Question
Can an unprivileged LST depositor enter through `external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)` while controlling asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior and send ETH directly to permissive receive-style functions before an accounting read, causing `contracts/LRTDepositPool.sol::depositAsset` to break the invariant that donated ETH cannot be converted into attacker-owned principal beyond the donated amount; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for depositAsset, leading to protocol insolvency? Probe condition: queued buffer route; amount case 2 wei; timing same block after updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositAsset
- Entrypoint: external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)
- Attacker controls: asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior; scenario: send ETH directly to permissive receive-style functions before an accounting read; validation style: a fork test using current deployed balances and supported assets; probe condition: queued buffer route; amount case 2 wei; timing same block after updateRSETHPrice; caller model EOA caller
- Exploit idea: Use forked-mainnet state to exercise the direct ETH donation skew path against depositAsset and look for deposit limit breaking value conservation or liveness.
- Invariant to test: donated ETH cannot be converted into attacker-owned principal beyond the donated amount; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for depositAsset
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: fuzz deposits around getAssetCurrentLimit and assert total deposits never exceed the configured limit by more than intended rounding Use probe condition: queued buffer route; amount case 2 wei; timing same block after updateRSETHPrice; caller model EOA caller.
