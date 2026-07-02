# Q1706: receiveFromNodeDelegator Fee Mint Limit Boundary Withdrawal Liquidity LRTOracle P1706

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromNodeDelegator()` while controlling msg.value and timing relative to getTotalAssetDeposits and execute price updates at exactly fee-period or mint-period boundaries, causing `contracts/LRTDepositPool.sol::receiveFromNodeDelegator` to break the invariant that daily limits cannot be bypassed or permanently block legitimate minting; specifically, withdrawal liquidity must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator, leading to failure to deliver promised returns without principal loss? Probe condition: LRTOracle price route; amount case 1 gwei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromNodeDelegator
- Entrypoint: external payable receiveFromNodeDelegator()
- Attacker controls: msg.value and timing relative to getTotalAssetDeposits; scenario: execute price updates at exactly fee-period or mint-period boundaries; validation style: two transactions before and after updateRSETHPrice; probe condition: LRTOracle price route; amount case 1 gwei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller
- Exploit idea: Use two-step sequence to exercise the fee mint limit boundary path against receiveFromNodeDelegator and look for withdrawal liquidity breaking value conservation or liveness.
- Invariant to test: daily limits cannot be bypassed or permanently block legitimate minting; specifically, withdrawal liquidity must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: assert user-created demand cannot strand unrelated users by consuming liquidity accounting Use probe condition: LRTOracle price route; amount case 1 gwei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.
