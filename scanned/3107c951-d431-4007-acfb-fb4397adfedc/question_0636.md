# Q636: depositAsset Malformed Referral Payload Deposit Limit queued P0636

## Question
Can an unprivileged LST depositor enter through `external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)` while controlling asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior and supply very large or unusual referralId data on hot user flows, causing `contracts/LRTDepositPool.sol::depositAsset` to break the invariant that unbounded calldata cannot create block-stuffing or stop critical withdrawals; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for depositAsset, leading to permanent freezing of funds? Probe condition: queued buffer route; amount case 32 ether; timing same block after updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositAsset
- Entrypoint: external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)
- Attacker controls: asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior; scenario: supply very large or unusual referralId data on hot user flows; validation style: attacker-created state followed by an honest operator action; probe condition: queued buffer route; amount case 32 ether; timing same block after updateRSETHPrice; caller model EOA caller
- Exploit idea: Use operator-normalization follow-up to exercise the malformed referral payload path against depositAsset and look for deposit limit breaking value conservation or liveness.
- Invariant to test: unbounded calldata cannot create block-stuffing or stop critical withdrawals; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for depositAsset
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: fuzz deposits around getAssetCurrentLimit and assert total deposits never exceed the configured limit by more than intended rounding Use probe condition: queued buffer route; amount case 32 ether; timing same block after updateRSETHPrice; caller model EOA caller.
