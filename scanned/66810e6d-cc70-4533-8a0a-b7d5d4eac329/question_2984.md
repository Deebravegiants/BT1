# Q2984: getAssetDistributionData Allowance Race Stale Balance rsETH P2984

## Question
Can an unprivileged depositor or caller of public view used by integrations enter through `depositAsset and oracle/accounting flows read getAssetDistributionData(asset)` while controlling asset, timing, and balances placed in pool/vault paths through public flows and change ERC20 allowance/balance between calculation and transfer using supported token behavior, causing `contracts/LRTDepositPool.sol::getAssetDistributionData` to break the invariant that protocol mints/burns only after actual spendable value is secured; specifically, stale balance must not violate backing, queue, yield, or liquidity accounting for getAssetDistributionData, leading to protocol insolvency? Probe condition: rsETH burn route; amount case 1 ether; timing one second after daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetDistributionData
- Entrypoint: depositAsset and oracle/accounting flows read getAssetDistributionData(asset)
- Attacker controls: asset, timing, and balances placed in pool/vault paths through public flows; scenario: change ERC20 allowance/balance between calculation and transfer using supported token behavior; validation style: compare ETH, stETH, and ETHx branches under the same value; probe condition: rsETH burn route; amount case 1 ether; timing one second after daily reset; caller model EOA caller
- Exploit idea: Use asset pair differential to exercise the allowance race path against getAssetDistributionData and look for stale balance breaking value conservation or liveness.
- Invariant to test: protocol mints/burns only after actual spendable value is secured; specifically, stale balance must not violate backing, queue, yield, or liquidity accounting for getAssetDistributionData
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: write a Foundry stateful test and assert protocol balances, liabilities, and user payouts remain conserved Use probe condition: rsETH burn route; amount case 1 ether; timing one second after daily reset; caller model EOA caller.
