# Q1682: receiveFromNodeDelegator Oracle Decimal Mismatch Price Update stETH P1682

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromNodeDelegator()` while controlling msg.value and timing relative to getTotalAssetDeposits and choose an asset flow whose oracle precision differs from 1e18 assumptions, causing `contracts/LRTDepositPool.sol::receiveFromNodeDelegator` to break the invariant that all share/asset conversions preserve value despite decimals; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator, leading to protocol insolvency? Probe condition: stETH supported asset route; amount case minAmount plus 1 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromNodeDelegator
- Entrypoint: external payable receiveFromNodeDelegator()
- Attacker controls: msg.value and timing relative to getTotalAssetDeposits; scenario: choose an asset flow whose oracle precision differs from 1e18 assumptions; validation style: two transactions before and after updateRSETHPrice; probe condition: stETH supported asset route; amount case minAmount plus 1 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller
- Exploit idea: Use two-step sequence to exercise the oracle decimal mismatch path against receiveFromNodeDelegator and look for price update breaking value conservation or liveness.
- Invariant to test: all share/asset conversions preserve value despite decimals; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: stETH supported asset route; amount case minAmount plus 1 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.
