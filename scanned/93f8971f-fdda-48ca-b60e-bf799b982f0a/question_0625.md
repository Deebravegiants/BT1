# Q625: depositAsset Malformed Referral Payload Rounding rsETH P0625

## Question
Can an unprivileged LST depositor enter through `external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)` while controlling asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior and supply very large or unusual referralId data on hot user flows, causing `contracts/LRTDepositPool.sol::depositAsset` to break the invariant that unbounded calldata cannot create block-stuffing or stop critical withdrawals; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for depositAsset, leading to direct theft of user funds? Probe condition: rsETH transfer route; amount case 32 ether; timing same block after updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositAsset
- Entrypoint: external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)
- Attacker controls: asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior; scenario: supply very large or unusual referralId data on hot user flows; validation style: one transaction using a contract wallet and controlled calldata; probe condition: rsETH transfer route; amount case 32 ether; timing same block after updateRSETHPrice; caller model EOA caller
- Exploit idea: Use single transaction to exercise the malformed referral payload path against depositAsset and look for rounding breaking value conservation or liveness.
- Invariant to test: unbounded calldata cannot create block-stuffing or stop critical withdrawals; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for depositAsset
- Expected Immunefi impact: Critical. Direct theft of any user funds, whether at-rest or in-motion, other than unclaimed yield
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: rsETH transfer route; amount case 32 ether; timing same block after updateRSETHPrice; caller model EOA caller.
