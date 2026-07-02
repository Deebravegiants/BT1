# Q1725: receiveFromNodeDelegator Aave Liquidity Shortfall Withdrawal Liquidity rsETH P1725

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromNodeDelegator()` while controlling msg.value and timing relative to getTotalAssetDeposits and complete or instant-withdraw ETH when Aave liquidity is lower than accounted aWETH principal, causing `contracts/LRTDepositPool.sol::receiveFromNodeDelegator` to break the invariant that external liquidity shortfall cannot burn rsETH without paying or freeze completed requests unexpectedly; specifically, withdrawal liquidity must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator, leading to failure to deliver promised returns without principal loss? Probe condition: rsETH transfer route; amount case 0.001 ether; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromNodeDelegator
- Entrypoint: external payable receiveFromNodeDelegator()
- Attacker controls: msg.value and timing relative to getTotalAssetDeposits; scenario: complete or instant-withdraw ETH when Aave liquidity is lower than accounted aWETH principal; validation style: warp/block-roll around day or withdrawal-delay boundaries; probe condition: rsETH transfer route; amount case 0.001 ether; timing at withdrawalDelayBlocks plus 1; caller model EOA caller
- Exploit idea: Use period boundary fuzz to exercise the Aave liquidity shortfall path against receiveFromNodeDelegator and look for withdrawal liquidity breaking value conservation or liveness.
- Invariant to test: external liquidity shortfall cannot burn rsETH without paying or freeze completed requests unexpectedly; specifically, withdrawal liquidity must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: assert user-created demand cannot strand unrelated users by consuming liquidity accounting Use probe condition: rsETH transfer route; amount case 0.001 ether; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.
