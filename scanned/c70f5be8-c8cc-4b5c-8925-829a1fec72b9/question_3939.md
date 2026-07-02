# Q3939: getAssetPrice Pause Boundary Race Oracle Lido P3939

## Question
Can an unprivileged depositor or withdrawer enter through `deposit/withdraw paths read getAssetPrice(asset)` while controlling asset choice, timing, and transaction sequence around public price updates and race a public action around a pause or public price-triggered pause transition, causing `contracts/LRTOracle.sol::getAssetPrice` to break the invariant that paused state cannot leave assets burned, committed, or transferred without corresponding settlement; specifically, oracle must not violate backing, queue, yield, or liquidity accounting for getAssetPrice, leading to direct theft of user funds? Probe condition: Lido stETH unstake route; amount case available liquidity exactly; timing immediately after direct ETH donation; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::getAssetPrice
- Entrypoint: deposit/withdraw paths read getAssetPrice(asset)
- Attacker controls: asset choice, timing, and transaction sequence around public price updates; scenario: race a public action around a pause or public price-triggered pause transition; validation style: a helper contract batching allowed public calls; probe condition: Lido stETH unstake route; amount case available liquidity exactly; timing immediately after direct ETH donation; caller model EOA caller
- Exploit idea: Use batched multicall-style sequence to exercise the pause boundary race path against getAssetPrice and look for oracle breaking value conservation or liveness.
- Invariant to test: paused state cannot leave assets burned, committed, or transferred without corresponding settlement; specifically, oracle must not violate backing, queue, yield, or liquidity accounting for getAssetPrice
- Expected Immunefi impact: Critical. Direct theft of any user funds, whether at-rest or in-motion, other than unclaimed yield
- Fast validation: mock the configured price fetcher within sane bounds and assert conversions conserve normalized value Use probe condition: Lido stETH unstake route; amount case available liquidity exactly; timing immediately after direct ETH donation; caller model EOA caller.
