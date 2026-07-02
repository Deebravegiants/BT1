# Q508: depositAsset Nonce Collision Attempt Deposit Limit LRTConverter P0508

## Question
Can an unprivileged LST depositor enter through `external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)` while controlling asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior and create requests across assets/accounts so nonce-derived ids collide or are consumed out of order, causing `contracts/LRTDepositPool.sol::depositAsset` to break the invariant that request ids remain unique per asset and cannot release another user request; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for depositAsset, leading to temporary freezing of funds? Probe condition: LRTConverter ETH-in-withdrawal route; amount case 1 gwei; timing same block after updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositAsset
- Entrypoint: external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)
- Attacker controls: asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior; scenario: create requests across assets/accounts so nonce-derived ids collide or are consumed out of order; validation style: a fork test using current deployed balances and supported assets; probe condition: LRTConverter ETH-in-withdrawal route; amount case 1 gwei; timing same block after updateRSETHPrice; caller model EOA caller
- Exploit idea: Use forked-mainnet state to exercise the nonce collision attempt path against depositAsset and look for deposit limit breaking value conservation or liveness.
- Invariant to test: request ids remain unique per asset and cannot release another user request; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for depositAsset
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: fuzz deposits around getAssetCurrentLimit and assert total deposits never exceed the configured limit by more than intended rounding Use probe condition: LRTConverter ETH-in-withdrawal route; amount case 1 gwei; timing same block after updateRSETHPrice; caller model EOA caller.
