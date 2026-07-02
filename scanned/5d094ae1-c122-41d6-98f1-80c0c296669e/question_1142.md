# Q1142: receiveFromRewardReceiver Block Timestamp Boundary Donation Accounting stETH P1142

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromRewardReceiver()` while controlling msg.value and direct call ordering before updateRSETHPrice and execute calls exactly at delay, daily reset, or period boundary blocks, causing `contracts/LRTDepositPool.sol::receiveFromRewardReceiver` to break the invariant that boundary equality cannot bypass delay, limits, or settlement ordering; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver, leading to protocol insolvency? Probe condition: stETH supported asset route; amount case available liquidity plus 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromRewardReceiver
- Entrypoint: external payable receiveFromRewardReceiver()
- Attacker controls: msg.value and direct call ordering before updateRSETHPrice; scenario: execute calls exactly at delay, daily reset, or period boundary blocks; validation style: two transactions before and after updateRSETHPrice; probe condition: stETH supported asset route; amount case available liquidity plus 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller
- Exploit idea: Use two-step sequence to exercise the block-timestamp boundary path against receiveFromRewardReceiver and look for donation accounting breaking value conservation or liveness.
- Invariant to test: boundary equality cannot bypass delay, limits, or settlement ordering; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: compare attacker donation cost to any increased redeemable value after price update Use probe condition: stETH supported asset route; amount case available liquidity plus 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.
