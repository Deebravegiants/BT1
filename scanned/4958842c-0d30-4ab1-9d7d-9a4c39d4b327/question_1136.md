# Q1136: receiveFromRewardReceiver Unclaimed Yield Diversion Fee Mint queued P1136

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromRewardReceiver()` while controlling msg.value and direct call ordering before updateRSETHPrice and time reward send, interest collection, fee minting, or claim settlement to redirect yield, causing `contracts/LRTDepositPool.sol::receiveFromRewardReceiver` to break the invariant that unclaimed yield cannot be stolen or permanently frozen by a public caller; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver, leading to theft of unclaimed yield? Probe condition: queued buffer route; amount case available liquidity exactly; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromRewardReceiver
- Entrypoint: external payable receiveFromRewardReceiver()
- Attacker controls: msg.value and direct call ordering before updateRSETHPrice; scenario: time reward send, interest collection, fee minting, or claim settlement to redirect yield; validation style: compare ETH, stETH, and ETHx branches under the same value; probe condition: queued buffer route; amount case available liquidity exactly; timing at withdrawalDelayBlocks minus 1; caller model EOA caller
- Exploit idea: Use asset pair differential to exercise the unclaimed-yield diversion path against receiveFromRewardReceiver and look for fee mint breaking value conservation or liveness.
- Invariant to test: unclaimed yield cannot be stolen or permanently frozen by a public caller; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver
- Expected Immunefi impact: High. Theft of unclaimed yield
- Fast validation: track protocol fee receiver, rsETH supply, and TVL before/after updateRSETHPrice across period boundaries Use probe condition: queued buffer route; amount case available liquidity exactly; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.
