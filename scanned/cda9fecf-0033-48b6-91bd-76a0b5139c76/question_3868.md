# Q3868: getAssetPrice Round Up Insolvency Oracle LRTConverter P3868

## Question
Can an unprivileged depositor or withdrawer enter through `deposit/withdraw paths read getAssetPrice(asset)` while controlling asset choice, timing, and transaction sequence around public price updates and choose amounts just above precision boundaries so liabilities round up while assets round down, causing `contracts/LRTOracle.sol::getAssetPrice` to break the invariant that rsETH liabilities never exceed normalized protocol assets; specifically, oracle must not violate backing, queue, yield, or liquidity accounting for getAssetPrice, leading to direct theft of user funds? Probe condition: LRTConverter ETH-in-withdrawal route; amount case daily limit minus 1 wei; timing immediately after direct ETH donation; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::getAssetPrice
- Entrypoint: deposit/withdraw paths read getAssetPrice(asset)
- Attacker controls: asset choice, timing, and transaction sequence around public price updates; scenario: choose amounts just above precision boundaries so liabilities round up while assets round down; validation style: a fork test using current deployed balances and supported assets; probe condition: LRTConverter ETH-in-withdrawal route; amount case daily limit minus 1 wei; timing immediately after direct ETH donation; caller model EOA caller
- Exploit idea: Use forked-mainnet state to exercise the round-up insolvency path against getAssetPrice and look for oracle breaking value conservation or liveness.
- Invariant to test: rsETH liabilities never exceed normalized protocol assets; specifically, oracle must not violate backing, queue, yield, or liquidity accounting for getAssetPrice
- Expected Immunefi impact: Critical. Direct theft of any user funds, whether at-rest or in-motion, other than unclaimed yield
- Fast validation: mock the configured price fetcher within sane bounds and assert conversions conserve normalized value Use probe condition: LRTConverter ETH-in-withdrawal route; amount case daily limit minus 1 wei; timing immediately after direct ETH donation; caller model EOA caller.
