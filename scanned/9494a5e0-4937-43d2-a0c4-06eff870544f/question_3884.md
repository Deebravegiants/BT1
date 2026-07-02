# Q3884: getAssetPrice Zero Or Dust Edge Oracle rsETH P3884

## Question
Can an unprivileged depositor or withdrawer enter through `deposit/withdraw paths read getAssetPrice(asset)` while controlling asset choice, timing, and transaction sequence around public price updates and use zero-like, one-wei, or min-threshold-adjacent amounts to bypass accounting updates, causing `contracts/LRTOracle.sol::getAssetPrice` to break the invariant that dust inputs cannot create withdrawable value or stuck committed assets; specifically, oracle must not violate backing, queue, yield, or liquidity accounting for getAssetPrice, leading to direct theft of user funds? Probe condition: rsETH burn route; amount case daily limit exactly; timing immediately after direct ETH donation; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::getAssetPrice
- Entrypoint: deposit/withdraw paths read getAssetPrice(asset)
- Attacker controls: asset choice, timing, and transaction sequence around public price updates; scenario: use zero-like, one-wei, or min-threshold-adjacent amounts to bypass accounting updates; validation style: compare ETH, stETH, and ETHx branches under the same value; probe condition: rsETH burn route; amount case daily limit exactly; timing immediately after direct ETH donation; caller model EOA caller
- Exploit idea: Use asset pair differential to exercise the zero-or-dust edge path against getAssetPrice and look for oracle breaking value conservation or liveness.
- Invariant to test: dust inputs cannot create withdrawable value or stuck committed assets; specifically, oracle must not violate backing, queue, yield, or liquidity accounting for getAssetPrice
- Expected Immunefi impact: Critical. Direct theft of any user funds, whether at-rest or in-motion, other than unclaimed yield
- Fast validation: mock the configured price fetcher within sane bounds and assert conversions conserve normalized value Use probe condition: rsETH burn route; amount case daily limit exactly; timing immediately after direct ETH donation; caller model EOA caller.
