# Q3019: getAssetDistributionData Unexpected Receiver Revert Converter Desync Lido P3019

## Question
Can an unprivileged depositor or caller of public view used by integrations enter through `depositAsset and oracle/accounting flows read getAssetDistributionData(asset)` while controlling asset, timing, and balances placed in pool/vault paths through public flows and use a receiver contract that rejects ETH or token callbacks during completion, causing `contracts/LRTDepositPool.sol::getAssetDistributionData` to break the invariant that one receiver cannot freeze protocol-wide funds or consume other users liquidity; specifically, converter desync must not violate backing, queue, yield, or liquidity accounting for getAssetDistributionData, leading to temporary freezing of funds? Probe condition: Lido stETH unstake route; amount case 31.999999 ether; timing one second after daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetDistributionData
- Entrypoint: depositAsset and oracle/accounting flows read getAssetDistributionData(asset)
- Attacker controls: asset, timing, and balances placed in pool/vault paths through public flows; scenario: use a receiver contract that rejects ETH or token callbacks during completion; validation style: an attacker contract as msg.sender or recipient; probe condition: Lido stETH unstake route; amount case 31.999999 ether; timing one second after daily reset; caller model EOA caller
- Exploit idea: Use receiver contract path to exercise the unexpected receiver revert path against getAssetDistributionData and look for converter desync breaking value conservation or liveness.
- Invariant to test: one receiver cannot freeze protocol-wide funds or consume other users liquidity; specifically, converter desync must not violate backing, queue, yield, or liquidity accounting for getAssetDistributionData
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: track ethValueInWithdrawal against converter assets/ETH after transfers, donations, and claims Use probe condition: Lido stETH unstake route; amount case 31.999999 ether; timing one second after daily reset; caller model EOA caller.
