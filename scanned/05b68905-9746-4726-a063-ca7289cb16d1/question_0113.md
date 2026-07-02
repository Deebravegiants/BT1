# Q113: depositETH Queue Head Blocking Deposit Limit Merkle-free P0113

## Question
Can an unprivileged ETH depositor enter through `external payable depositETH(minRSETHAmountExpected, referralId)` while controlling msg.value, minRSETHAmountExpected, referralId, call timing around public price updates and place a pathological first queue item that blocks later honest requests from completing, causing `contracts/LRTDepositPool.sol::depositETH` to break the invariant that one request cannot permanently or temporarily freeze unrelated user funds; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for depositETH, leading to temporary freezing of funds? Probe condition: Merkle-free yield accounting route; amount case 1 gwei; timing same block before updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositETH
- Entrypoint: external payable depositETH(minRSETHAmountExpected, referralId)
- Attacker controls: msg.value, minRSETHAmountExpected, referralId, call timing around public price updates; scenario: place a pathological first queue item that blocks later honest requests from completing; validation style: several attacker accounts creating adjacent requests; probe condition: Merkle-free yield accounting route; amount case 1 gwei; timing same block before updateRSETHPrice; caller model EOA caller
- Exploit idea: Use multi-account queue pressure to exercise the queue head blocking path against depositETH and look for deposit limit breaking value conservation or liveness.
- Invariant to test: one request cannot permanently or temporarily freeze unrelated user funds; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for depositETH
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: fuzz deposits around getAssetCurrentLimit and assert total deposits never exceed the configured limit by more than intended rounding Use probe condition: Merkle-free yield accounting route; amount case 1 gwei; timing same block before updateRSETHPrice; caller model EOA caller.
