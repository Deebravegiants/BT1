# Q1634: receiveFromNodeDelegator Pause Boundary Race Price Update deposit-limit P1634

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromNodeDelegator()` while controlling msg.value and timing relative to getTotalAssetDeposits and race a public action around a pause or public price-triggered pause transition, causing `contracts/LRTDepositPool.sol::receiveFromNodeDelegator` to break the invariant that paused state cannot leave assets burned, committed, or transferred without corresponding settlement; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator, leading to protocol insolvency? Probe condition: deposit-limit accounting route; amount case 2 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromNodeDelegator
- Entrypoint: external payable receiveFromNodeDelegator()
- Attacker controls: msg.value and timing relative to getTotalAssetDeposits; scenario: race a public action around a pause or public price-triggered pause transition; validation style: two transactions before and after updateRSETHPrice; probe condition: deposit-limit accounting route; amount case 2 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller
- Exploit idea: Use two-step sequence to exercise the pause boundary race path against receiveFromNodeDelegator and look for price update breaking value conservation or liveness.
- Invariant to test: paused state cannot leave assets burned, committed, or transferred without corresponding settlement; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: deposit-limit accounting route; amount case 2 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.
