# Q1878: receiveFromNodeDelegator Supply Zero Transition Price Update daily P1878

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromNodeDelegator()` while controlling msg.value and timing relative to getTotalAssetDeposits and operate around the transition from zero rsETH supply to nonzero supply or back toward zero, causing `contracts/LRTDepositPool.sol::receiveFromNodeDelegator` to break the invariant that initial price and final withdrawals cannot create unbacked supply or insolvency; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator, leading to protocol insolvency? Probe condition: daily fee mint limit route; amount case daily limit minus 1 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromNodeDelegator
- Entrypoint: external payable receiveFromNodeDelegator()
- Attacker controls: msg.value and timing relative to getTotalAssetDeposits; scenario: operate around the transition from zero rsETH supply to nonzero supply or back toward zero; validation style: compare many dust calls against one large call; probe condition: daily fee mint limit route; amount case daily limit minus 1 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller
- Exploit idea: Use dust-to-large differential to exercise the supply-zero transition path against receiveFromNodeDelegator and look for price update breaking value conservation or liveness.
- Invariant to test: initial price and final withdrawals cannot create unbacked supply or insolvency; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: daily fee mint limit route; amount case daily limit minus 1 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.
