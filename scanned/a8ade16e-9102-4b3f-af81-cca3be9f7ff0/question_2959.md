# Q2959: getAssetDistributionData Asset Identity Confusion Distribution Loop Lido P2959

## Question
Can an unprivileged depositor or caller of public view used by integrations enter through `depositAsset and oracle/accounting flows read getAssetDistributionData(asset)` while controlling asset, timing, and balances placed in pool/vault paths through public flows and use ETH sentinel, WETH, stETH, ETHx, or unsupported token addresses at branch boundaries, causing `contracts/LRTDepositPool.sol::getAssetDistributionData` to break the invariant that ETH and ERC20 branches cannot be confused to transfer or account the wrong asset; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetDistributionData, leading to temporary freezing of funds? Probe condition: Lido stETH unstake route; amount case 0.01 ether; timing one second after daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetDistributionData
- Entrypoint: depositAsset and oracle/accounting flows read getAssetDistributionData(asset)
- Attacker controls: asset, timing, and balances placed in pool/vault paths through public flows; scenario: use ETH sentinel, WETH, stETH, ETHx, or unsupported token addresses at branch boundaries; validation style: an attacker contract as msg.sender or recipient; probe condition: Lido stETH unstake route; amount case 0.01 ether; timing one second after daily reset; caller model EOA caller
- Exploit idea: Use receiver contract path to exercise the asset identity confusion path against getAssetDistributionData and look for distribution loop breaking value conservation or liveness.
- Invariant to test: ETH and ERC20 branches cannot be confused to transfer or account the wrong asset; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetDistributionData
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: measure loops over nodeDelegatorQueue/user queues and assert bounded gas under max configured counts Use probe condition: Lido stETH unstake route; amount case 0.01 ether; timing one second after daily reset; caller model EOA caller.
