# Q1731: receiveFromNodeDelegator Buffer Under Reservation Deposit Limit EigenLayer P1731

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromNodeDelegator()` while controlling msg.value and timing relative to getTotalAssetDeposits and create instant withdrawal demand while queued withdrawal buffer is stale or too low, causing `contracts/LRTDepositPool.sol::receiveFromNodeDelegator` to break the invariant that instant withdrawals cannot consume assets reserved for queued users; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator, leading to temporary freezing of funds? Probe condition: EigenLayer queued-withdrawal route; amount case 0.001 ether; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromNodeDelegator
- Entrypoint: external payable receiveFromNodeDelegator()
- Attacker controls: msg.value and timing relative to getTotalAssetDeposits; scenario: create instant withdrawal demand while queued withdrawal buffer is stale or too low; validation style: a helper contract batching allowed public calls; probe condition: EigenLayer queued-withdrawal route; amount case 0.001 ether; timing at withdrawalDelayBlocks plus 1; caller model EOA caller
- Exploit idea: Use batched multicall-style sequence to exercise the buffer under-reservation path against receiveFromNodeDelegator and look for deposit limit breaking value conservation or liveness.
- Invariant to test: instant withdrawals cannot consume assets reserved for queued users; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: fuzz deposits around getAssetCurrentLimit and assert total deposits never exceed the configured limit by more than intended rounding Use probe condition: EigenLayer queued-withdrawal route; amount case 0.001 ether; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.
