# Q1604: receiveFromNodeDelegator Fee On Transfer Token Skew Donation Accounting rsETH P1604

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromNodeDelegator()` while controlling msg.value and timing relative to getTotalAssetDeposits and use a supported ERC20 path where received balance is lower than depositAmount or transfer amount, causing `contracts/LRTDepositPool.sol::receiveFromNodeDelegator` to break the invariant that minted rsETH and committed withdrawals are based on actual assets received; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator, leading to permanent freezing of funds? Probe condition: rsETH burn route; amount case 1 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromNodeDelegator
- Entrypoint: external payable receiveFromNodeDelegator()
- Attacker controls: msg.value and timing relative to getTotalAssetDeposits; scenario: use a supported ERC20 path where received balance is lower than depositAmount or transfer amount; validation style: compare ETH, stETH, and ETHx branches under the same value; probe condition: rsETH burn route; amount case 1 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller
- Exploit idea: Use asset pair differential to exercise the fee-on-transfer token skew path against receiveFromNodeDelegator and look for donation accounting breaking value conservation or liveness.
- Invariant to test: minted rsETH and committed withdrawals are based on actual assets received; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: compare attacker donation cost to any increased redeemable value after price update Use probe condition: rsETH burn route; amount case 1 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.
