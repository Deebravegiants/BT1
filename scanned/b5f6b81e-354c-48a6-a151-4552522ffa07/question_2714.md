# Q2714: getAssetDistributionData Round Up Insolvency Stale Balance deposit-limit P2714

## Question
Can an unprivileged depositor or caller of public view used by integrations enter through `depositAsset and oracle/accounting flows read getAssetDistributionData(asset)` while controlling asset, timing, and balances placed in pool/vault paths through public flows and choose amounts just above precision boundaries so liabilities round up while assets round down, causing `contracts/LRTDepositPool.sol::getAssetDistributionData` to break the invariant that rsETH liabilities never exceed normalized protocol assets; specifically, stale balance must not violate backing, queue, yield, or liquidity accounting for getAssetDistributionData, leading to temporary freezing of funds? Probe condition: deposit-limit accounting route; amount case available liquidity minus 1 wei; timing exactly at daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetDistributionData
- Entrypoint: depositAsset and oracle/accounting flows read getAssetDistributionData(asset)
- Attacker controls: asset, timing, and balances placed in pool/vault paths through public flows; scenario: choose amounts just above precision boundaries so liabilities round up while assets round down; validation style: two transactions before and after updateRSETHPrice; probe condition: deposit-limit accounting route; amount case available liquidity minus 1 wei; timing exactly at daily reset; caller model EOA caller
- Exploit idea: Use two-step sequence to exercise the round-up insolvency path against getAssetDistributionData and look for stale balance breaking value conservation or liveness.
- Invariant to test: rsETH liabilities never exceed normalized protocol assets; specifically, stale balance must not violate backing, queue, yield, or liquidity accounting for getAssetDistributionData
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: write a Foundry stateful test and assert protocol balances, liabilities, and user payouts remain conserved Use probe condition: deposit-limit accounting route; amount case available liquidity minus 1 wei; timing exactly at daily reset; caller model EOA caller.
