# Q2834: getAssetDistributionData Oracle Decimal Mismatch Converter Desync deposit-limit P2834

## Question
Can an unprivileged depositor or caller of public view used by integrations enter through `depositAsset and oracle/accounting flows read getAssetDistributionData(asset)` while controlling asset, timing, and balances placed in pool/vault paths through public flows and choose an asset flow whose oracle precision differs from 1e18 assumptions, causing `contracts/LRTDepositPool.sol::getAssetDistributionData` to break the invariant that all share/asset conversions preserve value despite decimals; specifically, converter desync must not violate backing, queue, yield, or liquidity accounting for getAssetDistributionData, leading to temporary freezing of funds? Probe condition: deposit-limit accounting route; amount case 2 wei; timing one second after daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetDistributionData
- Entrypoint: depositAsset and oracle/accounting flows read getAssetDistributionData(asset)
- Attacker controls: asset, timing, and balances placed in pool/vault paths through public flows; scenario: choose an asset flow whose oracle precision differs from 1e18 assumptions; validation style: two transactions before and after updateRSETHPrice; probe condition: deposit-limit accounting route; amount case 2 wei; timing one second after daily reset; caller model EOA caller
- Exploit idea: Use two-step sequence to exercise the oracle decimal mismatch path against getAssetDistributionData and look for converter desync breaking value conservation or liveness.
- Invariant to test: all share/asset conversions preserve value despite decimals; specifically, converter desync must not violate backing, queue, yield, or liquidity accounting for getAssetDistributionData
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: track ethValueInWithdrawal against converter assets/ETH after transfers, donations, and claims Use probe condition: deposit-limit accounting route; amount case 2 wei; timing one second after daily reset; caller model EOA caller.
