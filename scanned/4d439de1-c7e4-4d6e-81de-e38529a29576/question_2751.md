# Q2751: getAssetDistributionData Fee On Transfer Token Skew Gas Growth EigenLayer P2751

## Question
Can an unprivileged depositor or caller of public view used by integrations enter through `depositAsset and oracle/accounting flows read getAssetDistributionData(asset)` while controlling asset, timing, and balances placed in pool/vault paths through public flows and use a supported ERC20 path where received balance is lower than depositAmount or transfer amount, causing `contracts/LRTDepositPool.sol::getAssetDistributionData` to break the invariant that minted rsETH and committed withdrawals are based on actual assets received; specifically, gas growth must not violate backing, queue, yield, or liquidity accounting for getAssetDistributionData, leading to unbounded gas consumption? Probe condition: EigenLayer queued-withdrawal route; amount case available liquidity plus 1 wei; timing exactly at daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetDistributionData
- Entrypoint: depositAsset and oracle/accounting flows read getAssetDistributionData(asset)
- Attacker controls: asset, timing, and balances placed in pool/vault paths through public flows; scenario: use a supported ERC20 path where received balance is lower than depositAmount or transfer amount; validation style: a helper contract batching allowed public calls; probe condition: EigenLayer queued-withdrawal route; amount case available liquidity plus 1 wei; timing exactly at daily reset; caller model EOA caller
- Exploit idea: Use batched multicall-style sequence to exercise the fee-on-transfer token skew path against getAssetDistributionData and look for gas growth breaking value conservation or liveness.
- Invariant to test: minted rsETH and committed withdrawals are based on actual assets received; specifically, gas growth must not violate backing, queue, yield, or liquidity accounting for getAssetDistributionData
- Expected Immunefi impact: Medium. Unbounded gas consumption
- Fast validation: grow attacker-controlled queues/arrays and measure whether settlement exceeds block gas limits Use probe condition: EigenLayer queued-withdrawal route; amount case available liquidity plus 1 wei; timing exactly at daily reset; caller model EOA caller.
