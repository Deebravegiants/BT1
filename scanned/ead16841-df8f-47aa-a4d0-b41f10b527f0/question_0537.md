# Q537: depositAsset Oracle Decimal Mismatch Rounding daily P0537

## Question
Can an unprivileged LST depositor enter through `external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)` while controlling asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior and choose an asset flow whose oracle precision differs from 1e18 assumptions, causing `contracts/LRTDepositPool.sol::depositAsset` to break the invariant that all share/asset conversions preserve value despite decimals; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for depositAsset, leading to direct theft of user funds? Probe condition: daily mint limit route; amount case 0.001 ether; timing same block after updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::depositAsset
- Entrypoint: external depositAsset(asset, depositAmount, minRSETHAmountExpected, referralId)
- Attacker controls: asset, depositAmount, allowance, minRSETHAmountExpected, referralId, ERC20 return behavior; scenario: choose an asset flow whose oracle precision differs from 1e18 assumptions; validation style: warp/block-roll around day or withdrawal-delay boundaries; probe condition: daily mint limit route; amount case 0.001 ether; timing same block after updateRSETHPrice; caller model EOA caller
- Exploit idea: Use period boundary fuzz to exercise the oracle decimal mismatch path against depositAsset and look for rounding breaking value conservation or liveness.
- Invariant to test: all share/asset conversions preserve value despite decimals; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for depositAsset
- Expected Immunefi impact: Critical. Direct theft of any user funds, whether at-rest or in-motion, other than unclaimed yield
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: daily mint limit route; amount case 0.001 ether; timing same block after updateRSETHPrice; caller model EOA caller.
