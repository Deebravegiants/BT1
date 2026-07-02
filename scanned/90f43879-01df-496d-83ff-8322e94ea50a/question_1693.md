# Q1693: receiveFromNodeDelegator Highest Price Ratchet Price Update Merkle-free P1693

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromNodeDelegator()` while controlling msg.value and timing relative to getTotalAssetDeposits and cause highestRsethPrice to ratchet from donated or transient balances then later reverse, causing `contracts/LRTDepositPool.sol::receiveFromNodeDelegator` to break the invariant that price protection cannot freeze funds or make withdrawals insolvent from transient TVL; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator, leading to protocol insolvency? Probe condition: Merkle-free yield accounting route; amount case minAmount plus 1 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromNodeDelegator
- Entrypoint: external payable receiveFromNodeDelegator()
- Attacker controls: msg.value and timing relative to getTotalAssetDeposits; scenario: cause highestRsethPrice to ratchet from donated or transient balances then later reverse; validation style: one transaction using a contract wallet and controlled calldata; probe condition: Merkle-free yield accounting route; amount case minAmount plus 1 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller
- Exploit idea: Use single transaction to exercise the highest-price ratchet path against receiveFromNodeDelegator and look for price update breaking value conservation or liveness.
- Invariant to test: price protection cannot freeze funds or make withdrawals insolvent from transient TVL; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: Merkle-free yield accounting route; amount case minAmount plus 1 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.
