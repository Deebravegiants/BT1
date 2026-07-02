# Q1139: receiveFromRewardReceiver Unclaimed Yield Diversion Donation Accounting Lido P1139

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromRewardReceiver()` while controlling msg.value and direct call ordering before updateRSETHPrice and time reward send, interest collection, fee minting, or claim settlement to redirect yield, causing `contracts/LRTDepositPool.sol::receiveFromRewardReceiver` to break the invariant that unclaimed yield cannot be stolen or permanently frozen by a public caller; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver, leading to protocol insolvency? Probe condition: Lido stETH unstake route; amount case available liquidity exactly; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromRewardReceiver
- Entrypoint: external payable receiveFromRewardReceiver()
- Attacker controls: msg.value and direct call ordering before updateRSETHPrice; scenario: time reward send, interest collection, fee minting, or claim settlement to redirect yield; validation style: a local supported-token harness with configurable transfer behavior; probe condition: Lido stETH unstake route; amount case available liquidity exactly; timing at withdrawalDelayBlocks minus 1; caller model EOA caller
- Exploit idea: Use malicious ERC20 harness to exercise the unclaimed-yield diversion path against receiveFromRewardReceiver and look for donation accounting breaking value conservation or liveness.
- Invariant to test: unclaimed yield cannot be stolen or permanently frozen by a public caller; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: compare attacker donation cost to any increased redeemable value after price update Use probe condition: Lido stETH unstake route; amount case available liquidity exactly; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.
