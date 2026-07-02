# Q1436: receiveFromLRTConverter Min Amount Bypass Price Update queued P1436

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromLRTConverter()` while controlling msg.value and call ordering relative to ethValueInWithdrawal and set minRSETHAmountExpected or min expected asset values at boundary values while prices move, causing `contracts/LRTDepositPool.sol::receiveFromLRTConverter` to break the invariant that slippage guards protect users and cannot be weaponized into insolvency; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromLRTConverter, leading to temporary freezing of funds? Probe condition: queued buffer route; amount case 32 ether; timing at withdrawalDelayBlocks exactly; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromLRTConverter
- Entrypoint: external payable receiveFromLRTConverter()
- Attacker controls: msg.value and call ordering relative to ethValueInWithdrawal; scenario: set minRSETHAmountExpected or min expected asset values at boundary values while prices move; validation style: compare ETH, stETH, and ETHx branches under the same value; probe condition: queued buffer route; amount case 32 ether; timing at withdrawalDelayBlocks exactly; caller model EOA caller
- Exploit idea: Use asset pair differential to exercise the min-amount bypass path against receiveFromLRTConverter and look for price update breaking value conservation or liveness.
- Invariant to test: slippage guards protect users and cannot be weaponized into insolvency; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromLRTConverter
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: queued buffer route; amount case 32 ether; timing at withdrawalDelayBlocks exactly; caller model EOA caller.
