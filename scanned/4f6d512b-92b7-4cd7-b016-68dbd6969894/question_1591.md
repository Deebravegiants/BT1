# Q1591: receiveFromNodeDelegator Direct ETH Donation Skew Deposit Limit EigenLayer P1591

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromNodeDelegator()` while controlling msg.value and timing relative to getTotalAssetDeposits and send ETH directly to permissive receive-style functions before an accounting read, causing `contracts/LRTDepositPool.sol::receiveFromNodeDelegator` to break the invariant that donated ETH cannot be converted into attacker-owned principal beyond the donated amount; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator, leading to temporary freezing of funds? Probe condition: EigenLayer queued-withdrawal route; amount case deposit limit plus 1 wei; timing at withdrawalDelayBlocks exactly; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromNodeDelegator
- Entrypoint: external payable receiveFromNodeDelegator()
- Attacker controls: msg.value and timing relative to getTotalAssetDeposits; scenario: send ETH directly to permissive receive-style functions before an accounting read; validation style: an attacker contract as msg.sender or recipient; probe condition: EigenLayer queued-withdrawal route; amount case deposit limit plus 1 wei; timing at withdrawalDelayBlocks exactly; caller model EOA caller
- Exploit idea: Use receiver contract path to exercise the direct ETH donation skew path against receiveFromNodeDelegator and look for deposit limit breaking value conservation or liveness.
- Invariant to test: donated ETH cannot be converted into attacker-owned principal beyond the donated amount; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: fuzz deposits around getAssetCurrentLimit and assert total deposits never exceed the configured limit by more than intended rounding Use probe condition: EigenLayer queued-withdrawal route; amount case deposit limit plus 1 wei; timing at withdrawalDelayBlocks exactly; caller model EOA caller.
