# Q1686: receiveFromNodeDelegator Oracle Decimal Mismatch Price Update LRTOracle P1686

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromNodeDelegator()` while controlling msg.value and timing relative to getTotalAssetDeposits and choose an asset flow whose oracle precision differs from 1e18 assumptions, causing `contracts/LRTDepositPool.sol::receiveFromNodeDelegator` to break the invariant that all share/asset conversions preserve value despite decimals; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator, leading to protocol insolvency? Probe condition: LRTOracle price route; amount case minAmount plus 1 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromNodeDelegator
- Entrypoint: external payable receiveFromNodeDelegator()
- Attacker controls: msg.value and timing relative to getTotalAssetDeposits; scenario: choose an asset flow whose oracle precision differs from 1e18 assumptions; validation style: compare many dust calls against one large call; probe condition: LRTOracle price route; amount case minAmount plus 1 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller
- Exploit idea: Use dust-to-large differential to exercise the oracle decimal mismatch path against receiveFromNodeDelegator and look for price update breaking value conservation or liveness.
- Invariant to test: all share/asset conversions preserve value despite decimals; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: LRTOracle price route; amount case minAmount plus 1 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.
