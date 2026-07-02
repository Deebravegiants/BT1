# Q2819: getAssetDistributionData Nonce Collision Attempt Distribution Loop Lido P2819

## Question
Can an unprivileged depositor or caller of public view used by integrations enter through `depositAsset and oracle/accounting flows read getAssetDistributionData(asset)` while controlling asset, timing, and balances placed in pool/vault paths through public flows and create requests across assets/accounts so nonce-derived ids collide or are consumed out of order, causing `contracts/LRTDepositPool.sol::getAssetDistributionData` to break the invariant that request ids remain unique per asset and cannot release another user request; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetDistributionData, leading to permanent freezing of funds? Probe condition: Lido stETH unstake route; amount case 1 wei; timing one second after daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetDistributionData
- Entrypoint: depositAsset and oracle/accounting flows read getAssetDistributionData(asset)
- Attacker controls: asset, timing, and balances placed in pool/vault paths through public flows; scenario: create requests across assets/accounts so nonce-derived ids collide or are consumed out of order; validation style: a local supported-token harness with configurable transfer behavior; probe condition: Lido stETH unstake route; amount case 1 wei; timing one second after daily reset; caller model EOA caller
- Exploit idea: Use malicious ERC20 harness to exercise the nonce collision attempt path against getAssetDistributionData and look for distribution loop breaking value conservation or liveness.
- Invariant to test: request ids remain unique per asset and cannot release another user request; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetDistributionData
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: measure loops over nodeDelegatorQueue/user queues and assert bounded gas under max configured counts Use probe condition: Lido stETH unstake route; amount case 1 wei; timing one second after daily reset; caller model EOA caller.
