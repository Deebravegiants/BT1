# Q2844: getAssetDistributionData Oracle Decimal Mismatch Stale Balance rsETH P2844

## Question
Can an unprivileged depositor or caller of public view used by integrations enter through `depositAsset and oracle/accounting flows read getAssetDistributionData(asset)` while controlling asset, timing, and balances placed in pool/vault paths through public flows and choose an asset flow whose oracle precision differs from 1e18 assumptions, causing `contracts/LRTDepositPool.sol::getAssetDistributionData` to break the invariant that all share/asset conversions preserve value despite decimals; specifically, stale balance must not violate backing, queue, yield, or liquidity accounting for getAssetDistributionData, leading to temporary freezing of funds? Probe condition: rsETH burn route; amount case minAmount minus 1 wei; timing one second after daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetDistributionData
- Entrypoint: depositAsset and oracle/accounting flows read getAssetDistributionData(asset)
- Attacker controls: asset, timing, and balances placed in pool/vault paths through public flows; scenario: choose an asset flow whose oracle precision differs from 1e18 assumptions; validation style: attacker-created state followed by an honest operator action; probe condition: rsETH burn route; amount case minAmount minus 1 wei; timing one second after daily reset; caller model EOA caller
- Exploit idea: Use operator-normalization follow-up to exercise the oracle decimal mismatch path against getAssetDistributionData and look for stale balance breaking value conservation or liveness.
- Invariant to test: all share/asset conversions preserve value despite decimals; specifically, stale balance must not violate backing, queue, yield, or liquidity accounting for getAssetDistributionData
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: write a Foundry stateful test and assert protocol balances, liabilities, and user payouts remain conserved Use probe condition: rsETH burn route; amount case minAmount minus 1 wei; timing one second after daily reset; caller model EOA caller.
