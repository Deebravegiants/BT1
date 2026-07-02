# Q2908: getAssetDistributionData Claim Replay Converter Desync LRTConverter P2908

## Question
Can an unprivileged depositor or caller of public view used by integrations enter through `depositAsset and oracle/accounting flows read getAssetDistributionData(asset)` while controlling asset, timing, and balances placed in pool/vault paths through public flows and repeat a claim, completion, or callback after state deletion or transfer occurs, causing `contracts/LRTDepositPool.sol::getAssetDistributionData` to break the invariant that one claim/request/NFT/token id settles at most once; specifically, converter desync must not violate backing, queue, yield, or liquidity accounting for getAssetDistributionData, leading to protocol insolvency? Probe condition: LRTConverter ETH-in-withdrawal route; amount case 1 gwei; timing one second after daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetDistributionData
- Entrypoint: depositAsset and oracle/accounting flows read getAssetDistributionData(asset)
- Attacker controls: asset, timing, and balances placed in pool/vault paths through public flows; scenario: repeat a claim, completion, or callback after state deletion or transfer occurs; validation style: a fork test using current deployed balances and supported assets; probe condition: LRTConverter ETH-in-withdrawal route; amount case 1 gwei; timing one second after daily reset; caller model EOA caller
- Exploit idea: Use forked-mainnet state to exercise the claim replay path against getAssetDistributionData and look for converter desync breaking value conservation or liveness.
- Invariant to test: one claim/request/NFT/token id settles at most once; specifically, converter desync must not violate backing, queue, yield, or liquidity accounting for getAssetDistributionData
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: track ethValueInWithdrawal against converter assets/ETH after transfers, donations, and claims Use probe condition: LRTConverter ETH-in-withdrawal route; amount case 1 gwei; timing one second after daily reset; caller model EOA caller.
