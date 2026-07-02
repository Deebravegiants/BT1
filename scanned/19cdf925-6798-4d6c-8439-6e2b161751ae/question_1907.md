# Q1907: receiveFromNodeDelegator Unclaimed Yield Diversion Donation Accounting FeeReceiver P1907

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromNodeDelegator()` while controlling msg.value and timing relative to getTotalAssetDeposits and time reward send, interest collection, fee minting, or claim settlement to redirect yield, causing `contracts/LRTDepositPool.sol::receiveFromNodeDelegator` to break the invariant that unclaimed yield cannot be stolen or permanently frozen by a public caller; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator, leading to permanent freezing of funds? Probe condition: FeeReceiver reward route; amount case available liquidity minus 1 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromNodeDelegator
- Entrypoint: external payable receiveFromNodeDelegator()
- Attacker controls: msg.value and timing relative to getTotalAssetDeposits; scenario: time reward send, interest collection, fee minting, or claim settlement to redirect yield; validation style: a local supported-token harness with configurable transfer behavior; probe condition: FeeReceiver reward route; amount case available liquidity minus 1 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller
- Exploit idea: Use malicious ERC20 harness to exercise the unclaimed-yield diversion path against receiveFromNodeDelegator and look for donation accounting breaking value conservation or liveness.
- Invariant to test: unclaimed yield cannot be stolen or permanently frozen by a public caller; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: compare attacker donation cost to any increased redeemable value after price update Use probe condition: FeeReceiver reward route; amount case available liquidity minus 1 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.
