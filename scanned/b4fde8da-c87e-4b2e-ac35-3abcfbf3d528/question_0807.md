# Q807: receiveFromRewardReceiver Zero Or Dust Edge Fee Mint FeeReceiver P0807

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromRewardReceiver()` while controlling msg.value and direct call ordering before updateRSETHPrice and use zero-like, one-wei, or min-threshold-adjacent amounts to bypass accounting updates, causing `contracts/LRTDepositPool.sol::receiveFromRewardReceiver` to break the invariant that dust inputs cannot create withdrawable value or stuck committed assets; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver, leading to theft of unclaimed yield? Probe condition: FeeReceiver reward route; amount case 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromRewardReceiver
- Entrypoint: external payable receiveFromRewardReceiver()
- Attacker controls: msg.value and direct call ordering before updateRSETHPrice; scenario: use zero-like, one-wei, or min-threshold-adjacent amounts to bypass accounting updates; validation style: a helper contract batching allowed public calls; probe condition: FeeReceiver reward route; amount case 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller
- Exploit idea: Use batched multicall-style sequence to exercise the zero-or-dust edge path against receiveFromRewardReceiver and look for fee mint breaking value conservation or liveness.
- Invariant to test: dust inputs cannot create withdrawable value or stuck committed assets; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver
- Expected Immunefi impact: High. Theft of unclaimed yield
- Fast validation: track protocol fee receiver, rsETH supply, and TVL before/after updateRSETHPrice across period boundaries Use probe condition: FeeReceiver reward route; amount case 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.
