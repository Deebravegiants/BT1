# Q2982: getAssetDistributionData Allowance Race Distribution Loop stETH P2982

## Question
Can an unprivileged depositor or caller of public view used by integrations enter through `depositAsset and oracle/accounting flows read getAssetDistributionData(asset)` while controlling asset, timing, and balances placed in pool/vault paths through public flows and change ERC20 allowance/balance between calculation and transfer using supported token behavior, causing `contracts/LRTDepositPool.sol::getAssetDistributionData` to break the invariant that protocol mints/burns only after actual spendable value is secured; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetDistributionData, leading to block stuffing? Probe condition: stETH supported asset route; amount case 1 ether; timing one second after daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetDistributionData
- Entrypoint: depositAsset and oracle/accounting flows read getAssetDistributionData(asset)
- Attacker controls: asset, timing, and balances placed in pool/vault paths through public flows; scenario: change ERC20 allowance/balance between calculation and transfer using supported token behavior; validation style: compare many dust calls against one large call; probe condition: stETH supported asset route; amount case 1 ether; timing one second after daily reset; caller model EOA caller
- Exploit idea: Use dust-to-large differential to exercise the allowance race path against getAssetDistributionData and look for distribution loop breaking value conservation or liveness.
- Invariant to test: protocol mints/burns only after actual spendable value is secured; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetDistributionData
- Expected Immunefi impact: Low. Block stuffing
- Fast validation: measure loops over nodeDelegatorQueue/user queues and assert bounded gas under max configured counts Use probe condition: stETH supported asset route; amount case 1 ether; timing one second after daily reset; caller model EOA caller.
