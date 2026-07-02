# Q769: receiveFromRewardReceiver Stale Price Sandwich Donation Accounting LRTUnstakingVault P0769

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromRewardReceiver()` while controlling msg.value and direct call ordering before updateRSETHPrice and sequence a small state-changing call before a public price update so mint and withdraw calculations use different rsETH or asset prices, causing `contracts/LRTDepositPool.sol::receiveFromRewardReceiver` to break the invariant that asset value and rsETH supply move consistently across the two legs; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver, leading to protocol insolvency? Probe condition: LRTUnstakingVault instant-liquidity route; amount case deposit limit minus 1 wei; timing same block after updateRSETHPrice; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromRewardReceiver
- Entrypoint: external payable receiveFromRewardReceiver()
- Attacker controls: msg.value and direct call ordering before updateRSETHPrice; scenario: sequence a small state-changing call before a public price update so mint and withdraw calculations use different rsETH or asset prices; validation style: one transaction using a contract wallet and controlled calldata; probe condition: LRTUnstakingVault instant-liquidity route; amount case deposit limit minus 1 wei; timing same block after updateRSETHPrice; caller model EOA caller
- Exploit idea: Use single transaction to exercise the stale-price sandwich path against receiveFromRewardReceiver and look for donation accounting breaking value conservation or liveness.
- Invariant to test: asset value and rsETH supply move consistently across the two legs; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: compare attacker donation cost to any increased redeemable value after price update Use probe condition: LRTUnstakingVault instant-liquidity route; amount case deposit limit minus 1 wei; timing same block after updateRSETHPrice; caller model EOA caller.
