# Q630: depositAsset Malformed Referral Payload Deposit Limit NodeDelegator P0630

## Question
Can an unprivileged LST depositor enter through `external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)` while controlling asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior and supply very large or unusual referralId data on hot user flows, causing `contracts/LRTDepositPool.sol::depositAsset` to break the invariant that unbounded calldata cannot create block-stuffing or stop critical withdrawals; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for depositAsset, leading to direct theft of user funds? Probe condition: NodeDelegator pod-share route; amount case 32 ether; timing same block after updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositAsset
- Entrypoint: external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)
- Attacker controls: asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior; scenario: supply very large or unusual referralId data on hot user flows; validation style: compare many dust calls against one large call; probe condition: NodeDelegator pod-share route; amount case 32 ether; timing same block after updateRSETHPrice; caller model EOA caller
- Exploit idea: Use dust-to-large differential to exercise the malformed referral payload path against depositAsset and look for deposit limit breaking value conservation or liveness.
- Invariant to test: unbounded calldata cannot create block-stuffing or stop critical withdrawals; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for depositAsset
- Expected Immunefi impact: Critical. Direct theft of any user funds, whether at-rest or in-motion, other than unclaimed yield
- Fast validation: fuzz deposits around getAssetCurrentLimit and assert total deposits never exceed the configured limit by more than intended rounding Use probe condition: NodeDelegator pod-share route; amount case 32 ether; timing same block after updateRSETHPrice; caller model EOA caller.
