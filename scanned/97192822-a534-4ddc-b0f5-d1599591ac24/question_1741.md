# Q1741: receiveFromNodeDelegator Buffer Over Reservation Price Update ETH P1741

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromNodeDelegator()` while controlling msg.value and timing relative to getTotalAssetDeposits and create queued withdrawal state that makes buffer reserve more than actual liabilities, causing `contracts/LRTDepositPool.sol::receiveFromNodeDelegator` to break the invariant that stale buffers cannot permanently freeze free liquidity; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator, leading to protocol insolvency? Probe condition: ETH sentinel route; amount case 0.01 ether; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromNodeDelegator
- Entrypoint: external payable receiveFromNodeDelegator()
- Attacker controls: msg.value and timing relative to getTotalAssetDeposits; scenario: create queued withdrawal state that makes buffer reserve more than actual liabilities; validation style: one transaction using a contract wallet and controlled calldata; probe condition: ETH sentinel route; amount case 0.01 ether; timing at withdrawalDelayBlocks plus 1; caller model EOA caller
- Exploit idea: Use single transaction to exercise the buffer over-reservation path against receiveFromNodeDelegator and look for price update breaking value conservation or liveness.
- Invariant to test: stale buffers cannot permanently freeze free liquidity; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: ETH sentinel route; amount case 0.01 ether; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.
