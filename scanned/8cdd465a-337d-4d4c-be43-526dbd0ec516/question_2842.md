# Q2842: getAssetDistributionData Oracle Decimal Mismatch Converter Desync stETH P2842

## Question
Can an unprivileged depositor or caller of public view used by integrations enter through `depositAsset and oracle/accounting flows read getAssetDistributionData(asset)` while controlling asset, timing, and balances placed in pool/vault paths through public flows and choose an asset flow whose oracle precision differs from 1e18 assumptions, causing `contracts/LRTDepositPool.sol::getAssetDistributionData` to break the invariant that all share/asset conversions preserve value despite decimals; specifically, converter desync must not violate backing, queue, yield, or liquidity accounting for getAssetDistributionData, leading to protocol insolvency? Probe condition: stETH supported asset route; amount case minAmount minus 1 wei; timing one second after daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetDistributionData
- Entrypoint: depositAsset and oracle/accounting flows read getAssetDistributionData(asset)
- Attacker controls: asset, timing, and balances placed in pool/vault paths through public flows; scenario: choose an asset flow whose oracle precision differs from 1e18 assumptions; validation style: stateful fuzzing over deposit, update price, withdraw, unlock, complete; probe condition: stETH supported asset route; amount case minAmount minus 1 wei; timing one second after daily reset; caller model EOA caller
- Exploit idea: Use stateful invariant fuzz to exercise the oracle decimal mismatch path against getAssetDistributionData and look for converter desync breaking value conservation or liveness.
- Invariant to test: all share/asset conversions preserve value despite decimals; specifically, converter desync must not violate backing, queue, yield, or liquidity accounting for getAssetDistributionData
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: track ethValueInWithdrawal against converter assets/ETH after transfers, donations, and claims Use probe condition: stETH supported asset route; amount case minAmount minus 1 wei; timing one second after daily reset; caller model EOA caller.
