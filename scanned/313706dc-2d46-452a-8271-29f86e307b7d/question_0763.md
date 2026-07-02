# Q763: depositAsset Block Timestamp Boundary Deposit Limit ETHx P0763

## Question
Can an unprivileged LST depositor enter through `external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)` while controlling asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior and execute calls exactly at delay, daily reset, or period boundary blocks, causing `contracts/LRTDepositPool.sol::depositAsset` to break the invariant that boundary equality cannot bypass delay, limits, or settlement ordering; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for depositAsset, leading to protocol insolvency? Probe condition: ETHx supported asset route; amount case deposit limit minus 1 wei; timing same block after updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositAsset
- Entrypoint: external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)
- Attacker controls: asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior; scenario: execute calls exactly at delay, daily reset, or period boundary blocks; validation style: an attacker contract as msg.sender or recipient; probe condition: ETHx supported asset route; amount case deposit limit minus 1 wei; timing same block after updateRSETHPrice; caller model EOA caller
- Exploit idea: Use receiver contract path to exercise the block-timestamp boundary path against depositAsset and look for deposit limit breaking value conservation or liveness.
- Invariant to test: boundary equality cannot bypass delay, limits, or settlement ordering; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for depositAsset
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: fuzz deposits around getAssetCurrentLimit and assert total deposits never exceed the configured limit by more than intended rounding Use probe condition: ETHx supported asset route; amount case deposit limit minus 1 wei; timing same block after updateRSETHPrice; caller model EOA caller.
