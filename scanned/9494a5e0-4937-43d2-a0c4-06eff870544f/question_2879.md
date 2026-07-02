# Q2879: getAssetDistributionData Aave Liquidity Shortfall Converter Desync Lido P2879

## Question
Can an unprivileged depositor or caller of public view used by integrations enter through `depositAsset and oracle/accounting flows read getAssetDistributionData(asset)` while controlling asset, timing, and balances placed in pool/vault paths through public flows and complete or instant-withdraw ETH when Aave liquidity is lower than accounted aWETH principal, causing `contracts/LRTDepositPool.sol::getAssetDistributionData` to break the invariant that external liquidity shortfall cannot burn rsETH without paying or freeze completed requests unexpectedly; specifically, converter desync must not violate backing, queue, yield, or liquidity accounting for getAssetDistributionData, leading to permanent freezing of funds? Probe condition: Lido stETH unstake route; amount case exact minAmount; timing one second after daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetDistributionData
- Entrypoint: depositAsset and oracle/accounting flows read getAssetDistributionData(asset)
- Attacker controls: asset, timing, and balances placed in pool/vault paths through public flows; scenario: complete or instant-withdraw ETH when Aave liquidity is lower than accounted aWETH principal; validation style: a local supported-token harness with configurable transfer behavior; probe condition: Lido stETH unstake route; amount case exact minAmount; timing one second after daily reset; caller model EOA caller
- Exploit idea: Use malicious ERC20 harness to exercise the Aave liquidity shortfall path against getAssetDistributionData and look for converter desync breaking value conservation or liveness.
- Invariant to test: external liquidity shortfall cannot burn rsETH without paying or freeze completed requests unexpectedly; specifically, converter desync must not violate backing, queue, yield, or liquidity accounting for getAssetDistributionData
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: track ethValueInWithdrawal against converter assets/ETH after transfers, donations, and claims Use probe condition: Lido stETH unstake route; amount case exact minAmount; timing one second after daily reset; caller model EOA caller.
