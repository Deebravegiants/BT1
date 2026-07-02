# Q3872: getAssetPrice Round Up Insolvency Rounding Aave P3872

## Question
Can an unprivileged depositor or withdrawer enter through `deposit/withdraw paths read getAssetPrice(asset)` while controlling asset choice, timing, and transaction sequence around public price updates and choose amounts just above precision boundaries so liabilities round up while assets round down, causing `contracts/LRTOracle.sol::getAssetPrice` to break the invariant that rsETH liabilities never exceed normalized protocol assets; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getAssetPrice, leading to failure to deliver promised returns without principal loss? Probe condition: Aave aWETH liquidity route; amount case daily limit minus 1 wei; timing immediately after direct ETH donation; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::getAssetPrice
- Entrypoint: deposit/withdraw paths read getAssetPrice(asset)
- Attacker controls: asset choice, timing, and transaction sequence around public price updates; scenario: choose amounts just above precision boundaries so liabilities round up while assets round down; validation style: compare ETH, stETH, and ETHx branches under the same value; probe condition: Aave aWETH liquidity route; amount case daily limit minus 1 wei; timing immediately after direct ETH donation; caller model EOA caller
- Exploit idea: Use asset pair differential to exercise the round-up insolvency path against getAssetPrice and look for rounding breaking value conservation or liveness.
- Invariant to test: rsETH liabilities never exceed normalized protocol assets; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for getAssetPrice
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: Aave aWETH liquidity route; amount case daily limit minus 1 wei; timing immediately after direct ETH donation; caller model EOA caller.
