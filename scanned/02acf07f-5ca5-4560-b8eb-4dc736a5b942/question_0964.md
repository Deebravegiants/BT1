# Q964: receiveFromRewardReceiver Buffer Under Reservation Reward Routing rsETH P0964

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromRewardReceiver()` while controlling msg.value and direct call ordering before updateRSETHPrice and create instant withdrawal demand while queued withdrawal buffer is stale or too low, causing `contracts/LRTDepositPool.sol::receiveFromRewardReceiver` to break the invariant that instant withdrawals cannot consume assets reserved for queued users; specifically, reward routing must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver, leading to failure to deliver promised returns without principal loss? Probe condition: rsETH burn route; amount case 0.1 ether; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromRewardReceiver
- Entrypoint: external payable receiveFromRewardReceiver()
- Attacker controls: msg.value and direct call ordering before updateRSETHPrice; scenario: create instant withdrawal demand while queued withdrawal buffer is stale or too low; validation style: a fork test using current deployed balances and supported assets; probe condition: rsETH burn route; amount case 0.1 ether; timing at withdrawalDelayBlocks minus 1; caller model EOA caller
- Exploit idea: Use forked-mainnet state to exercise the buffer under-reservation path against receiveFromRewardReceiver and look for reward routing breaking value conservation or liveness.
- Invariant to test: instant withdrawals cannot consume assets reserved for queued users; specifically, reward routing must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: send rewards/donations then call sendFunds and updateRSETHPrice, checking yield ownership Use probe condition: rsETH burn route; amount case 0.1 ether; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.
