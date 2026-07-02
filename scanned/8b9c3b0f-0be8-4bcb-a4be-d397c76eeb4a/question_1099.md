# Q1099: receiveFromRewardReceiver Unexpected Receiver Revert Fee Mint Lido P1099

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromRewardReceiver()` while controlling msg.value and direct call ordering before updateRSETHPrice and use a receiver contract that rejects ETH or token callbacks during completion, causing `contracts/LRTDepositPool.sol::receiveFromRewardReceiver` to break the invariant that one receiver cannot freeze protocol-wide funds or consume other users liquidity; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver, leading to theft of unclaimed yield? Probe condition: Lido stETH unstake route; amount case daily limit exactly; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromRewardReceiver
- Entrypoint: external payable receiveFromRewardReceiver()
- Attacker controls: msg.value and direct call ordering before updateRSETHPrice; scenario: use a receiver contract that rejects ETH or token callbacks during completion; validation style: an attacker contract as msg.sender or recipient; probe condition: Lido stETH unstake route; amount case daily limit exactly; timing at withdrawalDelayBlocks minus 1; caller model EOA caller
- Exploit idea: Use receiver contract path to exercise the unexpected receiver revert path against receiveFromRewardReceiver and look for fee mint breaking value conservation or liveness.
- Invariant to test: one receiver cannot freeze protocol-wide funds or consume other users liquidity; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver
- Expected Immunefi impact: High. Theft of unclaimed yield
- Fast validation: track protocol fee receiver, rsETH supply, and TVL before/after updateRSETHPrice across period boundaries Use probe condition: Lido stETH unstake route; amount case daily limit exactly; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.
