# Q1563: receiveFromNodeDelegator Round Up Insolvency Donation Accounting ETHx P1563

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromNodeDelegator()` while controlling msg.value and timing relative to getTotalAssetDeposits and choose amounts just above precision boundaries so liabilities round up while assets round down, causing `contracts/LRTDepositPool.sol::receiveFromNodeDelegator` to break the invariant that rsETH liabilities never exceed normalized protocol assets; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator, leading to permanent freezing of funds? Probe condition: ETHx supported asset route; amount case deposit limit minus 1 wei; timing at withdrawalDelayBlocks exactly; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromNodeDelegator
- Entrypoint: external payable receiveFromNodeDelegator()
- Attacker controls: msg.value and timing relative to getTotalAssetDeposits; scenario: choose amounts just above precision boundaries so liabilities round up while assets round down; validation style: a helper contract batching allowed public calls; probe condition: ETHx supported asset route; amount case deposit limit minus 1 wei; timing at withdrawalDelayBlocks exactly; caller model EOA caller
- Exploit idea: Use batched multicall-style sequence to exercise the round-up insolvency path against receiveFromNodeDelegator and look for donation accounting breaking value conservation or liveness.
- Invariant to test: rsETH liabilities never exceed normalized protocol assets; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: compare attacker donation cost to any increased redeemable value after price update Use probe condition: ETHx supported asset route; amount case deposit limit minus 1 wei; timing at withdrawalDelayBlocks exactly; caller model EOA caller.
