# Q1347: receiveFromLRTConverter Buffer Under Reservation Price Update FeeReceiver P1347

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromLRTConverter()` while controlling msg.value and call ordering relative to ethValueInWithdrawal and create instant withdrawal demand while queued withdrawal buffer is stale or too low, causing `contracts/LRTDepositPool.sol::receiveFromLRTConverter` to break the invariant that instant withdrawals cannot consume assets reserved for queued users; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromLRTConverter, leading to temporary freezing of funds? Probe condition: FeeReceiver reward route; amount case 0.01 ether; timing at withdrawalDelayBlocks exactly; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromLRTConverter
- Entrypoint: external payable receiveFromLRTConverter()
- Attacker controls: msg.value and call ordering relative to ethValueInWithdrawal; scenario: create instant withdrawal demand while queued withdrawal buffer is stale or too low; validation style: a helper contract batching allowed public calls; probe condition: FeeReceiver reward route; amount case 0.01 ether; timing at withdrawalDelayBlocks exactly; caller model EOA caller
- Exploit idea: Use batched multicall-style sequence to exercise the buffer under-reservation path against receiveFromLRTConverter and look for price update breaking value conservation or liveness.
- Invariant to test: instant withdrawals cannot consume assets reserved for queued users; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromLRTConverter
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: FeeReceiver reward route; amount case 0.01 ether; timing at withdrawalDelayBlocks exactly; caller model EOA caller.
