# Q1738: receiveFromNodeDelegator Buffer Under Reservation Price Update daily P1738

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromNodeDelegator()` while controlling msg.value and timing relative to getTotalAssetDeposits and create instant withdrawal demand while queued withdrawal buffer is stale or too low, causing `contracts/LRTDepositPool.sol::receiveFromNodeDelegator` to break the invariant that instant withdrawals cannot consume assets reserved for queued users; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator, leading to protocol insolvency? Probe condition: daily fee mint limit route; amount case 0.001 ether; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromNodeDelegator
- Entrypoint: external payable receiveFromNodeDelegator()
- Attacker controls: msg.value and timing relative to getTotalAssetDeposits; scenario: create instant withdrawal demand while queued withdrawal buffer is stale or too low; validation style: stateful fuzzing over deposit, update price, withdraw, unlock, complete; probe condition: daily fee mint limit route; amount case 0.001 ether; timing at withdrawalDelayBlocks plus 1; caller model EOA caller
- Exploit idea: Use stateful invariant fuzz to exercise the buffer under-reservation path against receiveFromNodeDelegator and look for price update breaking value conservation or liveness.
- Invariant to test: instant withdrawals cannot consume assets reserved for queued users; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: daily fee mint limit route; amount case 0.001 ether; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.
