# Q1826: receiveFromNodeDelegator Allowance Race Price Update LRTOracle P1826

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromNodeDelegator()` while controlling msg.value and timing relative to getTotalAssetDeposits and change ERC20 allowance/balance between calculation and transfer using supported token behavior, causing `contracts/LRTDepositPool.sol::receiveFromNodeDelegator` to break the invariant that protocol mints/burns only after actual spendable value is secured; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator, leading to protocol insolvency? Probe condition: LRTOracle price route; amount case 32 ether; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromNodeDelegator
- Entrypoint: external payable receiveFromNodeDelegator()
- Attacker controls: msg.value and timing relative to getTotalAssetDeposits; scenario: change ERC20 allowance/balance between calculation and transfer using supported token behavior; validation style: two transactions before and after updateRSETHPrice; probe condition: LRTOracle price route; amount case 32 ether; timing at withdrawalDelayBlocks plus 1; caller model EOA caller
- Exploit idea: Use two-step sequence to exercise the allowance race path against receiveFromNodeDelegator and look for price update breaking value conservation or liveness.
- Invariant to test: protocol mints/burns only after actual spendable value is secured; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: LRTOracle price route; amount case 32 ether; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.
