# Q2724: getAssetDistributionData Round Up Insolvency Converter Desync rsETH P2724

## Question
Can an unprivileged depositor or caller of public view used by integrations enter through `depositAsset and oracle/accounting flows read getAssetDistributionData(asset)` while controlling asset, timing, and balances placed in pool/vault paths through public flows and choose amounts just above precision boundaries so liabilities round up while assets round down, causing `contracts/LRTDepositPool.sol::getAssetDistributionData` to break the invariant that rsETH liabilities never exceed normalized protocol assets; specifically, converter desync must not violate backing, queue, yield, or liquidity accounting for getAssetDistributionData, leading to temporary freezing of funds? Probe condition: rsETH burn route; amount case available liquidity exactly; timing exactly at daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetDistributionData
- Entrypoint: depositAsset and oracle/accounting flows read getAssetDistributionData(asset)
- Attacker controls: asset, timing, and balances placed in pool/vault paths through public flows; scenario: choose amounts just above precision boundaries so liabilities round up while assets round down; validation style: attacker-created state followed by an honest operator action; probe condition: rsETH burn route; amount case available liquidity exactly; timing exactly at daily reset; caller model EOA caller
- Exploit idea: Use operator-normalization follow-up to exercise the round-up insolvency path against getAssetDistributionData and look for converter desync breaking value conservation or liveness.
- Invariant to test: rsETH liabilities never exceed normalized protocol assets; specifically, converter desync must not violate backing, queue, yield, or liquidity accounting for getAssetDistributionData
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: track ethValueInWithdrawal against converter assets/ETH after transfers, donations, and claims Use probe condition: rsETH burn route; amount case available liquidity exactly; timing exactly at daily reset; caller model EOA caller.
