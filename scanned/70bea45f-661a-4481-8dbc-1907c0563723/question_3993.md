# Q3993: getAssetPrice Oracle Decimal Mismatch Oracle Merkle-free P3993

## Question
Can an unprivileged depositor or withdrawer enter through `deposit/withdraw paths read getAssetPrice(asset)` while controlling asset choice, timing, and transaction sequence around public price updates and choose an asset flow whose oracle precision differs from 1e18 assumptions, causing `contracts/LRTOracle.sol::getAssetPrice` to break the invariant that all share/asset conversions preserve value despite decimals; specifically, oracle must not violate backing, queue, yield, or liquidity accounting for getAssetPrice, leading to direct theft of user funds? Probe condition: Merkle-free yield accounting route; amount case deposit limit plus 1 wei; timing immediately after direct ETH donation; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::getAssetPrice
- Entrypoint: deposit/withdraw paths read getAssetPrice(asset)
- Attacker controls: asset choice, timing, and transaction sequence around public price updates; scenario: choose an asset flow whose oracle precision differs from 1e18 assumptions; validation style: warp/block-roll around day or withdrawal-delay boundaries; probe condition: Merkle-free yield accounting route; amount case deposit limit plus 1 wei; timing immediately after direct ETH donation; caller model EOA caller
- Exploit idea: Use period boundary fuzz to exercise the oracle decimal mismatch path against getAssetPrice and look for oracle breaking value conservation or liveness.
- Invariant to test: all share/asset conversions preserve value despite decimals; specifically, oracle must not violate backing, queue, yield, or liquidity accounting for getAssetPrice
- Expected Immunefi impact: Critical. Direct theft of any user funds, whether at-rest or in-motion, other than unclaimed yield
- Fast validation: mock the configured price fetcher within sane bounds and assert conversions conserve normalized value Use probe condition: Merkle-free yield accounting route; amount case deposit limit plus 1 wei; timing immediately after direct ETH donation; caller model EOA caller.
