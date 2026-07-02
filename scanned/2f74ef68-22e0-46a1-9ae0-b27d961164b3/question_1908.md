# Q1908: receiveFromNodeDelegator Unclaimed Yield Diversion Price Update LRTConverter P1908

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromNodeDelegator()` while controlling msg.value and timing relative to getTotalAssetDeposits and time reward send, interest collection, fee minting, or claim settlement to redirect yield, causing `contracts/LRTDepositPool.sol::receiveFromNodeDelegator` to break the invariant that unclaimed yield cannot be stolen or permanently frozen by a public caller; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator, leading to protocol insolvency? Probe condition: LRTConverter ETH-in-withdrawal route; amount case available liquidity minus 1 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromNodeDelegator
- Entrypoint: external payable receiveFromNodeDelegator()
- Attacker controls: msg.value and timing relative to getTotalAssetDeposits; scenario: time reward send, interest collection, fee minting, or claim settlement to redirect yield; validation style: attacker-created state followed by an honest operator action; probe condition: LRTConverter ETH-in-withdrawal route; amount case available liquidity minus 1 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller
- Exploit idea: Use operator-normalization follow-up to exercise the unclaimed-yield diversion path against receiveFromNodeDelegator and look for price update breaking value conservation or liveness.
- Invariant to test: unclaimed yield cannot be stolen or permanently frozen by a public caller; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: LRTConverter ETH-in-withdrawal route; amount case available liquidity minus 1 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.
