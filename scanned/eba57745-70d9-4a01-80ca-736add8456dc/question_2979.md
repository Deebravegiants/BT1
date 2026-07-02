# Q2979: getAssetDistributionData Allowance Race Asset Accounting Lido P2979

## Question
Can an unprivileged depositor or caller of public view used by integrations enter through `depositAsset and oracle/accounting flows read getAssetDistributionData(asset)` while controlling asset, timing, and balances placed in pool/vault paths through public flows and change ERC20 allowance/balance between calculation and transfer using supported token behavior, causing `contracts/LRTDepositPool.sol::getAssetDistributionData` to break the invariant that protocol mints/burns only after actual spendable value is secured; specifically, asset accounting must not violate backing, queue, yield, or liquidity accounting for getAssetDistributionData, leading to protocol insolvency? Probe condition: Lido stETH unstake route; amount case 0.1 ether; timing one second after daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetDistributionData
- Entrypoint: depositAsset and oracle/accounting flows read getAssetDistributionData(asset)
- Attacker controls: asset, timing, and balances placed in pool/vault paths through public flows; scenario: change ERC20 allowance/balance between calculation and transfer using supported token behavior; validation style: a helper contract batching allowed public calls; probe condition: Lido stETH unstake route; amount case 0.1 ether; timing one second after daily reset; caller model EOA caller
- Exploit idea: Use batched multicall-style sequence to exercise the allowance race path against getAssetDistributionData and look for asset accounting breaking value conservation or liveness.
- Invariant to test: protocol mints/burns only after actual spendable value is secured; specifically, asset accounting must not violate backing, queue, yield, or liquidity accounting for getAssetDistributionData
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: write a Foundry stateful test and assert protocol balances, liabilities, and user payouts remain conserved Use probe condition: Lido stETH unstake route; amount case 0.1 ether; timing one second after daily reset; caller model EOA caller.
