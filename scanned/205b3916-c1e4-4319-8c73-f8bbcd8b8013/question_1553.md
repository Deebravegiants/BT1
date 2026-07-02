# Q1553: receiveFromNodeDelegator Round Down Accumulation Price Update Merkle-free P1553

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromNodeDelegator()` while controlling msg.value and timing relative to getTotalAssetDeposits and split a large action into many dust-sized calls to accumulate rounding residue in the attacker direction, causing `contracts/LRTDepositPool.sol::receiveFromNodeDelegator` to break the invariant that sum of split outputs is not greater than one equivalent unsplit output; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator, leading to protocol insolvency? Probe condition: Merkle-free yield accounting route; amount case available liquidity plus 1 wei; timing at withdrawalDelayBlocks exactly; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromNodeDelegator
- Entrypoint: external payable receiveFromNodeDelegator()
- Attacker controls: msg.value and timing relative to getTotalAssetDeposits; scenario: split a large action into many dust-sized calls to accumulate rounding residue in the attacker direction; validation style: several attacker accounts creating adjacent requests; probe condition: Merkle-free yield accounting route; amount case available liquidity plus 1 wei; timing at withdrawalDelayBlocks exactly; caller model EOA caller
- Exploit idea: Use multi-account queue pressure to exercise the round-down accumulation path against receiveFromNodeDelegator and look for price update breaking value conservation or liveness.
- Invariant to test: sum of split outputs is not greater than one equivalent unsplit output; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: Merkle-free yield accounting route; amount case available liquidity plus 1 wei; timing at withdrawalDelayBlocks exactly; caller model EOA caller.
