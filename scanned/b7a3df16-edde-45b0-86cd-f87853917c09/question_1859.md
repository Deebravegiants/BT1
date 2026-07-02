# Q1859: receiveFromNodeDelegator Unbounded Event/data Growth Donation Accounting Lido P1859

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromNodeDelegator()` while controlling msg.value and timing relative to getTotalAssetDeposits and force huge arrays or strings through accepted inputs that are later used by automation, causing `contracts/LRTDepositPool.sol::receiveFromNodeDelegator` to break the invariant that accepted public inputs cannot cause block stuffing or persistent gas grief in settlement; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator, leading to permanent freezing of funds? Probe condition: Lido stETH unstake route; amount case 32.000001 ether; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromNodeDelegator
- Entrypoint: external payable receiveFromNodeDelegator()
- Attacker controls: msg.value and timing relative to getTotalAssetDeposits; scenario: force huge arrays or strings through accepted inputs that are later used by automation; validation style: a local supported-token harness with configurable transfer behavior; probe condition: Lido stETH unstake route; amount case 32.000001 ether; timing at withdrawalDelayBlocks plus 1; caller model EOA caller
- Exploit idea: Use malicious ERC20 harness to exercise the unbounded event/data growth path against receiveFromNodeDelegator and look for donation accounting breaking value conservation or liveness.
- Invariant to test: accepted public inputs cannot cause block stuffing or persistent gas grief in settlement; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: compare attacker donation cost to any increased redeemable value after price update Use probe condition: Lido stETH unstake route; amount case 32.000001 ether; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.
