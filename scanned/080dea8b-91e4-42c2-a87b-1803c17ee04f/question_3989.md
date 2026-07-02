# Q3989: getAssetPrice Oracle Decimal Mismatch Stale Price LRTUnstakingVault P3989

## Question
Can an unprivileged depositor or withdrawer enter through `deposit/withdraw paths read getAssetPrice(asset)` while controlling asset choice, timing, and transaction sequence around public price updates and choose an asset flow whose oracle precision differs from 1e18 assumptions, causing `contracts/LRTOracle.sol::getAssetPrice` to break the invariant that all share/asset conversions preserve value despite decimals; specifically, stale price must not violate backing, queue, yield, or liquidity accounting for getAssetPrice, leading to permanent freezing of funds? Probe condition: LRTUnstakingVault instant-liquidity route; amount case deposit limit plus 1 wei; timing immediately after direct ETH donation; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::getAssetPrice
- Entrypoint: deposit/withdraw paths read getAssetPrice(asset)
- Attacker controls: asset choice, timing, and transaction sequence around public price updates; scenario: choose an asset flow whose oracle precision differs from 1e18 assumptions; validation style: several attacker accounts creating adjacent requests; probe condition: LRTUnstakingVault instant-liquidity route; amount case deposit limit plus 1 wei; timing immediately after direct ETH donation; caller model EOA caller
- Exploit idea: Use multi-account queue pressure to exercise the oracle decimal mismatch path against getAssetPrice and look for stale price breaking value conservation or liveness.
- Invariant to test: all share/asset conversions preserve value despite decimals; specifically, stale price must not violate backing, queue, yield, or liquidity accounting for getAssetPrice
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: sequence price update/deposit/withdraw with stale and fresh prices and assert no profitable round trip. Use probe condition: LRTUnstakingVault instant-liquidity route; amount case deposit limit plus 1 wei; timing immediately after direct ETH donation; caller model EOA caller.
