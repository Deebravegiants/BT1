# Q1742: receiveFromNodeDelegator Buffer Over Reservation Deposit Limit stETH P1742

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromNodeDelegator()` while controlling msg.value and timing relative to getTotalAssetDeposits and create queued withdrawal state that makes buffer reserve more than actual liabilities, causing `contracts/LRTDepositPool.sol::receiveFromNodeDelegator` to break the invariant that stale buffers cannot permanently freeze free liquidity; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator, leading to temporary freezing of funds? Probe condition: stETH supported asset route; amount case 0.01 ether; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromNodeDelegator
- Entrypoint: external payable receiveFromNodeDelegator()
- Attacker controls: msg.value and timing relative to getTotalAssetDeposits; scenario: create queued withdrawal state that makes buffer reserve more than actual liabilities; validation style: two transactions before and after updateRSETHPrice; probe condition: stETH supported asset route; amount case 0.01 ether; timing at withdrawalDelayBlocks plus 1; caller model EOA caller
- Exploit idea: Use two-step sequence to exercise the buffer over-reservation path against receiveFromNodeDelegator and look for deposit limit breaking value conservation or liveness.
- Invariant to test: stale buffers cannot permanently freeze free liquidity; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: fuzz deposits around getAssetCurrentLimit and assert total deposits never exceed the configured limit by more than intended rounding Use probe condition: stETH supported asset route; amount case 0.01 ether; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.
