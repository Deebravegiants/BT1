# Q2836: getAssetDistributionData Oracle Decimal Mismatch Stale Balance queued P2836

## Question
Can an unprivileged depositor or caller of public view used by integrations enter through `depositAsset and oracle/accounting flows read getAssetDistributionData(asset)` while controlling asset, timing, and balances placed in pool/vault paths through public flows and choose an asset flow whose oracle precision differs from 1e18 assumptions, causing `contracts/LRTDepositPool.sol::getAssetDistributionData` to break the invariant that all share/asset conversions preserve value despite decimals; specifically, stale balance must not violate backing, queue, yield, or liquidity accounting for getAssetDistributionData, leading to permanent freezing of funds? Probe condition: queued buffer route; amount case 2 wei; timing one second after daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetDistributionData
- Entrypoint: depositAsset and oracle/accounting flows read getAssetDistributionData(asset)
- Attacker controls: asset, timing, and balances placed in pool/vault paths through public flows; scenario: choose an asset flow whose oracle precision differs from 1e18 assumptions; validation style: a fork test using current deployed balances and supported assets; probe condition: queued buffer route; amount case 2 wei; timing one second after daily reset; caller model EOA caller
- Exploit idea: Use forked-mainnet state to exercise the oracle decimal mismatch path against getAssetDistributionData and look for stale balance breaking value conservation or liveness.
- Invariant to test: all share/asset conversions preserve value despite decimals; specifically, stale balance must not violate backing, queue, yield, or liquidity accounting for getAssetDistributionData
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: write a Foundry stateful test and assert protocol balances, liabilities, and user payouts remain conserved Use probe condition: queued buffer route; amount case 2 wei; timing one second after daily reset; caller model EOA caller.
