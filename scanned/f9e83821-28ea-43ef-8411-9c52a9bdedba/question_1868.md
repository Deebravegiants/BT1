# Q1868: receiveFromNodeDelegator Unexpected Receiver Revert Deposit Limit LRTConverter P1868

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromNodeDelegator()` while controlling msg.value and timing relative to getTotalAssetDeposits and use a receiver contract that rejects ETH or token callbacks during completion, causing `contracts/LRTDepositPool.sol::receiveFromNodeDelegator` to break the invariant that one receiver cannot freeze protocol-wide funds or consume other users liquidity; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator, leading to temporary freezing of funds? Probe condition: LRTConverter ETH-in-withdrawal route; amount case daily limit minus 1 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromNodeDelegator
- Entrypoint: external payable receiveFromNodeDelegator()
- Attacker controls: msg.value and timing relative to getTotalAssetDeposits; scenario: use a receiver contract that rejects ETH or token callbacks during completion; validation style: compare ETH, stETH, and ETHx branches under the same value; probe condition: LRTConverter ETH-in-withdrawal route; amount case daily limit minus 1 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller
- Exploit idea: Use asset pair differential to exercise the unexpected receiver revert path against receiveFromNodeDelegator and look for deposit limit breaking value conservation or liveness.
- Invariant to test: one receiver cannot freeze protocol-wide funds or consume other users liquidity; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: fuzz deposits around getAssetCurrentLimit and assert total deposits never exceed the configured limit by more than intended rounding Use probe condition: LRTConverter ETH-in-withdrawal route; amount case daily limit minus 1 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.
