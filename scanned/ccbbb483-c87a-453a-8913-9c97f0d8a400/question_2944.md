# Q2944: getAssetDistributionData Gas Amplified Loop Distribution Loop rsETH P2944

## Question
Can an unprivileged depositor or caller of public view used by integrations enter through `depositAsset and oracle/accounting flows read getAssetDistributionData(asset)` while controlling asset, timing, and balances placed in pool/vault paths through public flows and grow a user-controlled queue/list then trigger a function that iterates it in a critical flow, causing `contracts/LRTDepositPool.sol::getAssetDistributionData` to break the invariant that user-controlled growth remains bounded and cannot cause unbounded gas consumption; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetDistributionData, leading to block stuffing? Probe condition: rsETH burn route; amount case 0.01 ether; timing one second after daily reset; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::getAssetDistributionData
- Entrypoint: depositAsset and oracle/accounting flows read getAssetDistributionData(asset)
- Attacker controls: asset, timing, and balances placed in pool/vault paths through public flows; scenario: grow a user-controlled queue/list then trigger a function that iterates it in a critical flow; validation style: a fork test using current deployed balances and supported assets; probe condition: rsETH burn route; amount case 0.01 ether; timing one second after daily reset; caller model EOA caller
- Exploit idea: Use forked-mainnet state to exercise the gas-amplified loop path against getAssetDistributionData and look for distribution loop breaking value conservation or liveness.
- Invariant to test: user-controlled growth remains bounded and cannot cause unbounded gas consumption; specifically, distribution loop must not violate backing, queue, yield, or liquidity accounting for getAssetDistributionData
- Expected Immunefi impact: Low. Block stuffing
- Fast validation: measure loops over nodeDelegatorQueue/user queues and assert bounded gas under max configured counts Use probe condition: rsETH burn route; amount case 0.01 ether; timing one second after daily reset; caller model EOA caller.
