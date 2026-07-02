# Q1815: receiveFromNodeDelegator Min Amount Bypass Price Update withdrawal P1815

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromNodeDelegator()` while controlling msg.value and timing relative to getTotalAssetDeposits and set minRSETHAmountExpected or min expected asset values at boundary values while prices move, causing `contracts/LRTDepositPool.sol::receiveFromNodeDelegator` to break the invariant that slippage guards protect users and cannot be weaponized into insolvency; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator, leading to protocol insolvency? Probe condition: withdrawal request nonce route; amount case 31.999999 ether; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromNodeDelegator
- Entrypoint: external payable receiveFromNodeDelegator()
- Attacker controls: msg.value and timing relative to getTotalAssetDeposits; scenario: set minRSETHAmountExpected or min expected asset values at boundary values while prices move; validation style: a helper contract batching allowed public calls; probe condition: withdrawal request nonce route; amount case 31.999999 ether; timing at withdrawalDelayBlocks plus 1; caller model EOA caller
- Exploit idea: Use batched multicall-style sequence to exercise the min-amount bypass path against receiveFromNodeDelegator and look for price update breaking value conservation or liveness.
- Invariant to test: slippage guards protect users and cannot be weaponized into insolvency; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: withdrawal request nonce route; amount case 31.999999 ether; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.
