# Q1915: receiveFromNodeDelegator Block Timestamp Boundary Price Update withdrawal P1915

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromNodeDelegator()` while controlling msg.value and timing relative to getTotalAssetDeposits and execute calls exactly at delay, daily reset, or period boundary blocks, causing `contracts/LRTDepositPool.sol::receiveFromNodeDelegator` to break the invariant that boundary equality cannot bypass delay, limits, or settlement ordering; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator, leading to protocol insolvency? Probe condition: withdrawal request nonce route; amount case available liquidity minus 1 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromNodeDelegator
- Entrypoint: external payable receiveFromNodeDelegator()
- Attacker controls: msg.value and timing relative to getTotalAssetDeposits; scenario: execute calls exactly at delay, daily reset, or period boundary blocks; validation style: an attacker contract as msg.sender or recipient; probe condition: withdrawal request nonce route; amount case available liquidity minus 1 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller
- Exploit idea: Use receiver contract path to exercise the block-timestamp boundary path against receiveFromNodeDelegator and look for price update breaking value conservation or liveness.
- Invariant to test: boundary equality cannot bypass delay, limits, or settlement ordering; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: withdrawal request nonce route; amount case available liquidity minus 1 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.
