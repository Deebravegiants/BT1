# Q1808: receiveFromNodeDelegator Asset Identity Confusion Price Update LRTConverter P1808

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromNodeDelegator()` while controlling msg.value and timing relative to getTotalAssetDeposits and use ETH sentinel, WETH, stETH, ETHx, or unsupported token addresses at branch boundaries, causing `contracts/LRTDepositPool.sol::receiveFromNodeDelegator` to break the invariant that ETH and ERC20 branches cannot be confused to transfer or account the wrong asset; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator, leading to protocol insolvency? Probe condition: LRTConverter ETH-in-withdrawal route; amount case 31.999999 ether; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromNodeDelegator
- Entrypoint: external payable receiveFromNodeDelegator()
- Attacker controls: msg.value and timing relative to getTotalAssetDeposits; scenario: use ETH sentinel, WETH, stETH, ETHx, or unsupported token addresses at branch boundaries; validation style: compare ETH, stETH, and ETHx branches under the same value; probe condition: LRTConverter ETH-in-withdrawal route; amount case 31.999999 ether; timing at withdrawalDelayBlocks plus 1; caller model EOA caller
- Exploit idea: Use asset pair differential to exercise the asset identity confusion path against receiveFromNodeDelegator and look for price update breaking value conservation or liveness.
- Invariant to test: ETH and ERC20 branches cannot be confused to transfer or account the wrong asset; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: LRTConverter ETH-in-withdrawal route; amount case 31.999999 ether; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.
