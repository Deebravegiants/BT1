# Q1708: receiveFromNodeDelegator Fee Mint Limit Boundary Price Update LRTConverter P1708

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromNodeDelegator()` while controlling msg.value and timing relative to getTotalAssetDeposits and execute price updates at exactly fee-period or mint-period boundaries, causing `contracts/LRTDepositPool.sol::receiveFromNodeDelegator` to break the invariant that daily limits cannot be bypassed or permanently block legitimate minting; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator, leading to protocol insolvency? Probe condition: LRTConverter ETH-in-withdrawal route; amount case 1 gwei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromNodeDelegator
- Entrypoint: external payable receiveFromNodeDelegator()
- Attacker controls: msg.value and timing relative to getTotalAssetDeposits; scenario: execute price updates at exactly fee-period or mint-period boundaries; validation style: a fork test using current deployed balances and supported assets; probe condition: LRTConverter ETH-in-withdrawal route; amount case 1 gwei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller
- Exploit idea: Use forked-mainnet state to exercise the fee mint limit boundary path against receiveFromNodeDelegator and look for price update breaking value conservation or liveness.
- Invariant to test: daily limits cannot be bypassed or permanently block legitimate minting; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: LRTConverter ETH-in-withdrawal route; amount case 1 gwei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.
