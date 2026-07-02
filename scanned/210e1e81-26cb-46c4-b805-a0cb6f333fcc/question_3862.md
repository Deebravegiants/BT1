# Q3862: getAssetPrice Round Down Accumulation Oracle stETH P3862

## Question
Can an unprivileged depositor or withdrawer enter through `deposit/withdraw paths read getAssetPrice(asset)` while controlling asset choice, timing, and transaction sequence around public price updates and split a large action into many dust-sized calls to accumulate rounding residue in the attacker direction, causing `contracts/LRTOracle.sol::getAssetPrice` to break the invariant that sum of split outputs is not greater than one equivalent unsplit output; specifically, oracle must not violate backing, queue, yield, or liquidity accounting for getAssetPrice, leading to direct theft of user funds? Probe condition: stETH supported asset route; amount case daily limit minus 1 wei; timing immediately after direct ETH donation; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::getAssetPrice
- Entrypoint: deposit/withdraw paths read getAssetPrice(asset)
- Attacker controls: asset choice, timing, and transaction sequence around public price updates; scenario: split a large action into many dust-sized calls to accumulate rounding residue in the attacker direction; validation style: stateful fuzzing over deposit, update price, withdraw, unlock, complete; probe condition: stETH supported asset route; amount case daily limit minus 1 wei; timing immediately after direct ETH donation; caller model EOA caller
- Exploit idea: Use stateful invariant fuzz to exercise the round-down accumulation path against getAssetPrice and look for oracle breaking value conservation or liveness.
- Invariant to test: sum of split outputs is not greater than one equivalent unsplit output; specifically, oracle must not violate backing, queue, yield, or liquidity accounting for getAssetPrice
- Expected Immunefi impact: Critical. Direct theft of any user funds, whether at-rest or in-motion, other than unclaimed yield
- Fast validation: mock the configured price fetcher within sane bounds and assert conversions conserve normalized value Use probe condition: stETH supported asset route; amount case daily limit minus 1 wei; timing immediately after direct ETH donation; caller model EOA caller.
