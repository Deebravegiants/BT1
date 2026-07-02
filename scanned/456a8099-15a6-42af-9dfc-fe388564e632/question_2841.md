# Q2841: getAssetDistributionData Oracle Decimal Mismatch Distribution Loop ETH P2841

## Question
Can an unprivileged depositor or caller of public view used by integrations enter through `depositAsset and oracle/accounting flows read getAssetDistributionData(asset)` while controlling asset, timing, and balances placed in pool/vault paths through public flows and choose an asset flow whose oracle precision differs from 1e18 assumptions, causing `contracts/LRTDepositPool.sol::getAssetDistributionData` to break the invariant that all share/asset conversions preserve value despite decimals; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetDistributionData, leading to permanent freezing of funds? Probe condition: ETH sentinel route; amount case minAmount minus 1 wei; timing one second after daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetDistributionData
- Entrypoint: depositAsset and oracle/accounting flows read getAssetDistributionData(asset)
- Attacker controls: asset, timing, and balances placed in pool/vault paths through public flows; scenario: choose an asset flow whose oracle precision differs from 1e18 assumptions; validation style: warp/block-roll around day or withdrawal-delay boundaries; probe condition: ETH sentinel route; amount case minAmount minus 1 wei; timing one second after daily reset; caller model EOA caller
- Exploit idea: Use period boundary fuzz to exercise the oracle decimal mismatch path against getAssetDistributionData and look for distribution loop breaking value conservation or liveness.
- Invariant to test: all share/asset conversions preserve value despite decimals; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetDistributionData
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: measure loops over nodeDelegatorQueue/user queues and assert bounded gas under max configured counts Use probe condition: ETH sentinel route; amount case minAmount minus 1 wei; timing one second after daily reset; caller model EOA caller.
