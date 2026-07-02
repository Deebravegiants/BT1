# Q935: receiveFromRewardReceiver Highest Price Ratchet Reward Routing withdrawal P0935

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromRewardReceiver()` while controlling msg.value and direct call ordering before updateRSETHPrice and cause highestRsethPrice to ratchet from donated or transient balances then later reverse, causing `contracts/LRTDepositPool.sol::receiveFromRewardReceiver` to break the invariant that price protection cannot freeze funds or make withdrawals insolvent from transient TVL; specifically, reward routing must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver, leading to failure to deliver promised returns without principal loss? Probe condition: withdrawal request nonce route; amount case 0.001 ether; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromRewardReceiver
- Entrypoint: external payable receiveFromRewardReceiver()
- Attacker controls: msg.value and direct call ordering before updateRSETHPrice; scenario: cause highestRsethPrice to ratchet from donated or transient balances then later reverse; validation style: a local supported-token harness with configurable transfer behavior; probe condition: withdrawal request nonce route; amount case 0.001 ether; timing at withdrawalDelayBlocks minus 1; caller model EOA caller
- Exploit idea: Use malicious ERC20 harness to exercise the highest-price ratchet path against receiveFromRewardReceiver and look for reward routing breaking value conservation or liveness.
- Invariant to test: price protection cannot freeze funds or make withdrawals insolvent from transient TVL; specifically, reward routing must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: send rewards/donations then call sendFunds and updateRSETHPrice, checking yield ownership Use probe condition: withdrawal request nonce route; amount case 0.001 ether; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.
