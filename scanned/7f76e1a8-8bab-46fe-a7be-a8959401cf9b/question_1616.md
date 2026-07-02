# Q1616: receiveFromNodeDelegator Rebasing Balance Drift Price Update queued P1616

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromNodeDelegator()` while controlling msg.value and timing relative to getTotalAssetDeposits and let a supported rebasing LST balance change between request creation and final settlement, causing `contracts/LRTDepositPool.sol::receiveFromNodeDelegator` to break the invariant that rebases cannot create unbacked rsETH or freeze queued withdrawals; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator, leading to protocol insolvency? Probe condition: queued buffer route; amount case 1 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromNodeDelegator
- Entrypoint: external payable receiveFromNodeDelegator()
- Attacker controls: msg.value and timing relative to getTotalAssetDeposits; scenario: let a supported rebasing LST balance change between request creation and final settlement; validation style: compare ETH, stETH, and ETHx branches under the same value; probe condition: queued buffer route; amount case 1 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller
- Exploit idea: Use asset pair differential to exercise the rebasing balance drift path against receiveFromNodeDelegator and look for price update breaking value conservation or liveness.
- Invariant to test: rebases cannot create unbacked rsETH or freeze queued withdrawals; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: queued buffer route; amount case 1 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.
