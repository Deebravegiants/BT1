# Q1148: receiveFromRewardReceiver Block Timestamp Boundary Price Update LRTConverter P1148

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromRewardReceiver()` while controlling msg.value and direct call ordering before updateRSETHPrice and execute calls exactly at delay, daily reset, or period boundary blocks, causing `contracts/LRTDepositPool.sol::receiveFromRewardReceiver` to break the invariant that boundary equality cannot bypass delay, limits, or settlement ordering; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver, leading to permanent freezing of unclaimed yield? Probe condition: LRTConverter ETH-in-withdrawal route; amount case available liquidity plus 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromRewardReceiver
- Entrypoint: external payable receiveFromRewardReceiver()
- Attacker controls: msg.value and direct call ordering before updateRSETHPrice; scenario: execute calls exactly at delay, daily reset, or period boundary blocks; validation style: compare ETH, stETH, and ETHx branches under the same value; probe condition: LRTConverter ETH-in-withdrawal route; amount case available liquidity plus 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller
- Exploit idea: Use asset pair differential to exercise the block-timestamp boundary path against receiveFromRewardReceiver and look for price update breaking value conservation or liveness.
- Invariant to test: boundary equality cannot bypass delay, limits, or settlement ordering; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver
- Expected Immunefi impact: Medium. Permanent freezing of unclaimed yield
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: LRTConverter ETH-in-withdrawal route; amount case available liquidity plus 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.
