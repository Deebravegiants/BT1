# Q771: receiveFromRewardReceiver Stale Price Sandwich Price Update EigenLayer P0771

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromRewardReceiver()` while controlling msg.value and direct call ordering before updateRSETHPrice and sequence a small state-changing call before a public price update so mint and withdraw calculations use different rsETH or asset prices, causing `contracts/LRTDepositPool.sol::receiveFromRewardReceiver` to break the invariant that asset value and rsETH supply move consistently across the two legs; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver, leading to permanent freezing of unclaimed yield? Probe condition: EigenLayer queued-withdrawal route; amount case deposit limit minus 1 wei; timing same block after updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromRewardReceiver
- Entrypoint: external payable receiveFromRewardReceiver()
- Attacker controls: msg.value and direct call ordering before updateRSETHPrice; scenario: sequence a small state-changing call before a public price update so mint and withdraw calculations use different rsETH or asset prices; validation style: a helper contract batching allowed public calls; probe condition: EigenLayer queued-withdrawal route; amount case deposit limit minus 1 wei; timing same block after updateRSETHPrice; caller model EOA caller
- Exploit idea: Use batched multicall-style sequence to exercise the stale-price sandwich path against receiveFromRewardReceiver and look for price update breaking value conservation or liveness.
- Invariant to test: asset value and rsETH supply move consistently across the two legs; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver
- Expected Immunefi impact: Medium. Permanent freezing of unclaimed yield
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: EigenLayer queued-withdrawal route; amount case deposit limit minus 1 wei; timing same block after updateRSETHPrice; caller model EOA caller.
