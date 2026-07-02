# Q1820: receiveFromNodeDelegator Min Amount Bypass Deposit Limit Swell P1820

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromNodeDelegator()` while controlling msg.value and timing relative to getTotalAssetDeposits and set minRSETHAmountExpected or min expected asset values at boundary values while prices move, causing `contracts/LRTDepositPool.sol::receiveFromNodeDelegator` to break the invariant that slippage guards protect users and cannot be weaponized into insolvency; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator, leading to temporary freezing of funds? Probe condition: Swell swETH legacy route; amount case 31.999999 ether; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromNodeDelegator
- Entrypoint: external payable receiveFromNodeDelegator()
- Attacker controls: msg.value and timing relative to getTotalAssetDeposits; scenario: set minRSETHAmountExpected or min expected asset values at boundary values while prices move; validation style: compare ETH, stETH, and ETHx branches under the same value; probe condition: Swell swETH legacy route; amount case 31.999999 ether; timing at withdrawalDelayBlocks plus 1; caller model EOA caller
- Exploit idea: Use asset pair differential to exercise the min-amount bypass path against receiveFromNodeDelegator and look for deposit limit breaking value conservation or liveness.
- Invariant to test: slippage guards protect users and cannot be weaponized into insolvency; specifically, deposit limit must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: fuzz deposits around getAssetCurrentLimit and assert total deposits never exceed the configured limit by more than intended rounding Use probe condition: Swell swETH legacy route; amount case 31.999999 ether; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.
