# Q477: depositAsset Reentrant Token Callback Fee On Transfer daily P0477

## Question
Can an unprivileged LST depositor enter through `external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)` while controlling asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior and use an ERC777-like or malicious token callback during safeTransferFrom/safeTransfer to reenter another public protocol path, causing `contracts/LRTDepositPool.sol::depositAsset` to break the invariant that nonReentrant and state ordering prevent double mint, double claim, or liquidity theft; specifically, fee on transfer must not violate backing, queue, yield, or liquidity accounting for depositAsset, leading to direct theft of user funds? Probe condition: daily mint limit route; amount case exact minAmount; timing same block after updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositAsset
- Entrypoint: external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)
- Attacker controls: asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior; scenario: use an ERC777-like or malicious token callback during safeTransferFrom/safeTransfer to reenter another public protocol path; validation style: warp/block-roll around day or withdrawal-delay boundaries; probe condition: daily mint limit route; amount case exact minAmount; timing same block after updateRSETHPrice; caller model EOA caller
- Exploit idea: Use period boundary fuzz to exercise the reentrant token callback path against depositAsset and look for fee on transfer breaking value conservation or liveness.
- Invariant to test: nonReentrant and state ordering prevent double mint, double claim, or liquidity theft; specifically, fee on transfer must not violate backing, queue, yield, or liquidity accounting for depositAsset
- Expected Immunefi impact: Critical. Direct theft of any user funds, whether at-rest or in-motion, other than unclaimed yield
- Fast validation: support a local fee-on-transfer token in a fork harness and assert actual received amount is used Use probe condition: daily mint limit route; amount case exact minAmount; timing same block after updateRSETHPrice; caller model EOA caller.
