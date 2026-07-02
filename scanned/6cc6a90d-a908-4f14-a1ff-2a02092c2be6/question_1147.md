# Q1147: receiveFromRewardReceiver Block Timestamp Boundary Fee Mint FeeReceiver P1147

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromRewardReceiver()` while controlling msg.value and direct call ordering before updateRSETHPrice and execute calls exactly at delay, daily reset, or period boundary blocks, causing `contracts/LRTDepositPool.sol::receiveFromRewardReceiver` to break the invariant that boundary equality cannot bypass delay, limits, or settlement ordering; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver, leading to theft of unclaimed yield? Probe condition: FeeReceiver reward route; amount case available liquidity plus 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromRewardReceiver
- Entrypoint: external payable receiveFromRewardReceiver()
- Attacker controls: msg.value and direct call ordering before updateRSETHPrice; scenario: execute calls exactly at delay, daily reset, or period boundary blocks; validation style: an attacker contract as msg.sender or recipient; probe condition: FeeReceiver reward route; amount case available liquidity plus 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller
- Exploit idea: Use receiver contract path to exercise the block-timestamp boundary path against receiveFromRewardReceiver and look for fee mint breaking value conservation or liveness.
- Invariant to test: boundary equality cannot bypass delay, limits, or settlement ordering; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver
- Expected Immunefi impact: High. Theft of unclaimed yield
- Fast validation: track protocol fee receiver, rsETH supply, and TVL before/after updateRSETHPrice across period boundaries Use probe condition: FeeReceiver reward route; amount case available liquidity plus 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.
