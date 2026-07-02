# Q983: receiveFromRewardReceiver Buffer Over Reservation Reward Routing ETHx P0983

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromRewardReceiver()` while controlling msg.value and direct call ordering before updateRSETHPrice and create queued withdrawal state that makes buffer reserve more than actual liabilities, causing `contracts/LRTDepositPool.sol::receiveFromRewardReceiver` to break the invariant that stale buffers cannot permanently freeze free liquidity; specifically, reward routing must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver, leading to failure to deliver promised returns without principal loss? Probe condition: ETHx supported asset route; amount case 1 ether; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromRewardReceiver
- Entrypoint: external payable receiveFromRewardReceiver()
- Attacker controls: msg.value and direct call ordering before updateRSETHPrice; scenario: create queued withdrawal state that makes buffer reserve more than actual liabilities; validation style: a local supported-token harness with configurable transfer behavior; probe condition: ETHx supported asset route; amount case 1 ether; timing at withdrawalDelayBlocks minus 1; caller model EOA caller
- Exploit idea: Use malicious ERC20 harness to exercise the buffer over-reservation path against receiveFromRewardReceiver and look for reward routing breaking value conservation or liveness.
- Invariant to test: stale buffers cannot permanently freeze free liquidity; specifically, reward routing must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: send rewards/donations then call sendFunds and updateRSETHPrice, checking yield ownership Use probe condition: ETHx supported asset route; amount case 1 ether; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.
