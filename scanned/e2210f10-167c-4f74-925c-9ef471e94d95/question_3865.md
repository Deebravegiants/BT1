# Q3865: getAssetPrice Round Up Insolvency Decimals rsETH P3865

## Question
Can an unprivileged depositor or withdrawer enter through `deposit/withdraw paths read getAssetPrice(asset)` while controlling asset choice, timing, and transaction sequence around public price updates and choose amounts just above precision boundaries so liabilities round up while assets round down, causing `contracts/LRTOracle.sol::getAssetPrice` to break the invariant that rsETH liabilities never exceed normalized protocol assets; specifically, decimals must not violate backing, queue, yield, or liquidity accounting for getAssetPrice, leading to protocol insolvency? Probe condition: rsETH transfer route; amount case daily limit minus 1 wei; timing immediately after direct ETH donation; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::getAssetPrice
- Entrypoint: deposit/withdraw paths read getAssetPrice(asset)
- Attacker controls: asset choice, timing, and transaction sequence around public price updates; scenario: choose amounts just above precision boundaries so liabilities round up while assets round down; validation style: one transaction using a contract wallet and controlled calldata; probe condition: rsETH transfer route; amount case daily limit minus 1 wei; timing immediately after direct ETH donation; caller model EOA caller
- Exploit idea: Use single transaction to exercise the round-up insolvency path against getAssetPrice and look for decimals breaking value conservation or liveness.
- Invariant to test: rsETH liabilities never exceed normalized protocol assets; specifically, decimals must not violate backing, queue, yield, or liquidity accounting for getAssetPrice
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: fuzz oracle precision and token decimals assumptions and assert 1e18 normalization is consistent Use probe condition: rsETH transfer route; amount case daily limit minus 1 wei; timing immediately after direct ETH donation; caller model EOA caller.
