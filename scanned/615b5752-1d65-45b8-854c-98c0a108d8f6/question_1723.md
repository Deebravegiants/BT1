# Q1723: receiveFromNodeDelegator Aave Liquidity Shortfall Price Update ETHx P1723

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromNodeDelegator()` while controlling msg.value and timing relative to getTotalAssetDeposits and complete or instant-withdraw ETH when Aave liquidity is lower than accounted aWETH principal, causing `contracts/LRTDepositPool.sol::receiveFromNodeDelegator` to break the invariant that external liquidity shortfall cannot burn rsETH without paying or freeze completed requests unexpectedly; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator, leading to protocol insolvency? Probe condition: ETHx supported asset route; amount case 0.001 ether; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromNodeDelegator
- Entrypoint: external payable receiveFromNodeDelegator()
- Attacker controls: msg.value and timing relative to getTotalAssetDeposits; scenario: complete or instant-withdraw ETH when Aave liquidity is lower than accounted aWETH principal; validation style: an attacker contract as msg.sender or recipient; probe condition: ETHx supported asset route; amount case 0.001 ether; timing at withdrawalDelayBlocks plus 1; caller model EOA caller
- Exploit idea: Use receiver contract path to exercise the Aave liquidity shortfall path against receiveFromNodeDelegator and look for price update breaking value conservation or liveness.
- Invariant to test: external liquidity shortfall cannot burn rsETH without paying or freeze completed requests unexpectedly; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: ETHx supported asset route; amount case 0.001 ether; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.
