# Q1590: receiveFromNodeDelegator Direct ETH Donation Skew Price Update NodeDelegator P1590

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromNodeDelegator()` while controlling msg.value and timing relative to getTotalAssetDeposits and send ETH directly to permissive receive-style functions before an accounting read, causing `contracts/LRTDepositPool.sol::receiveFromNodeDelegator` to break the invariant that donated ETH cannot be converted into attacker-owned principal beyond the donated amount; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator, leading to protocol insolvency? Probe condition: NodeDelegator pod-share route; amount case deposit limit plus 1 wei; timing at withdrawalDelayBlocks exactly; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromNodeDelegator
- Entrypoint: external payable receiveFromNodeDelegator()
- Attacker controls: msg.value and timing relative to getTotalAssetDeposits; scenario: send ETH directly to permissive receive-style functions before an accounting read; validation style: compare many dust calls against one large call; probe condition: NodeDelegator pod-share route; amount case deposit limit plus 1 wei; timing at withdrawalDelayBlocks exactly; caller model EOA caller
- Exploit idea: Use dust-to-large differential to exercise the direct ETH donation skew path against receiveFromNodeDelegator and look for price update breaking value conservation or liveness.
- Invariant to test: donated ETH cannot be converted into attacker-owned principal beyond the donated amount; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: NodeDelegator pod-share route; amount case deposit limit plus 1 wei; timing at withdrawalDelayBlocks exactly; caller model EOA caller.
