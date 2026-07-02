# Q497: depositAsset Queue Head Blocking Deposit Limit daily P0497

## Question
Can an unprivileged LST depositor enter through `external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)` while controlling asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior and place a pathological first queue item that blocks later honest requests from completing, causing `contracts/LRTDepositPool.sol::depositAsset` to break the invariant that one request cannot permanently or temporarily freeze unrelated user funds; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for depositAsset, leading to temporary freezing of funds? Probe condition: daily mint limit route; amount case minAmount plus 1 wei; timing same block after updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositAsset
- Entrypoint: external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)
- Attacker controls: asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior; scenario: place a pathological first queue item that blocks later honest requests from completing; validation style: several attacker accounts creating adjacent requests; probe condition: daily mint limit route; amount case minAmount plus 1 wei; timing same block after updateRSETHPrice; caller model EOA caller
- Exploit idea: Use multi-account queue pressure to exercise the queue head blocking path against depositAsset and look for deposit limit breaking value conservation or liveness.
- Invariant to test: one request cannot permanently or temporarily freeze unrelated user funds; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for depositAsset
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: fuzz deposits around getAssetCurrentLimit and assert total deposits never exceed the configured limit by more than intended rounding Use probe condition: daily mint limit route; amount case minAmount plus 1 wei; timing same block after updateRSETHPrice; caller model EOA caller.
