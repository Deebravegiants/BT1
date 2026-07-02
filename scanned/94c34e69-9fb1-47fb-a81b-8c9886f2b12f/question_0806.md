# Q806: receiveFromRewardReceiver Zero Or Dust Edge Donation Accounting LRTOracle P0806

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromRewardReceiver()` while controlling msg.value and direct call ordering before updateRSETHPrice and use zero-like, one-wei, or min-threshold-adjacent amounts to bypass accounting updates, causing `contracts/LRTDepositPool.sol::receiveFromRewardReceiver` to break the invariant that dust inputs cannot create withdrawable value or stuck committed assets; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver, leading to protocol insolvency? Probe condition: LRTOracle price route; amount case 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromRewardReceiver
- Entrypoint: external payable receiveFromRewardReceiver()
- Attacker controls: msg.value and direct call ordering before updateRSETHPrice; scenario: use zero-like, one-wei, or min-threshold-adjacent amounts to bypass accounting updates; validation style: two transactions before and after updateRSETHPrice; probe condition: LRTOracle price route; amount case 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller
- Exploit idea: Use two-step sequence to exercise the zero-or-dust edge path against receiveFromRewardReceiver and look for donation accounting breaking value conservation or liveness.
- Invariant to test: dust inputs cannot create withdrawable value or stuck committed assets; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: compare attacker donation cost to any increased redeemable value after price update Use probe condition: LRTOracle price route; amount case 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.
