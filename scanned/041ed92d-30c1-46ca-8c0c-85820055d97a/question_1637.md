# Q1637: receiveFromNodeDelegator Pause Boundary Race Donation Accounting daily P1637

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromNodeDelegator()` while controlling msg.value and timing relative to getTotalAssetDeposits and race a public action around a pause or public price-triggered pause transition, causing `contracts/LRTDepositPool.sol::receiveFromNodeDelegator` to break the invariant that paused state cannot leave assets burned, committed, or transferred without corresponding settlement; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator, leading to permanent freezing of funds? Probe condition: daily mint limit route; amount case 2 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromNodeDelegator
- Entrypoint: external payable receiveFromNodeDelegator()
- Attacker controls: msg.value and timing relative to getTotalAssetDeposits; scenario: race a public action around a pause or public price-triggered pause transition; validation style: several attacker accounts creating adjacent requests; probe condition: daily mint limit route; amount case 2 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller
- Exploit idea: Use multi-account queue pressure to exercise the pause boundary race path against receiveFromNodeDelegator and look for donation accounting breaking value conservation or liveness.
- Invariant to test: paused state cannot leave assets burned, committed, or transferred without corresponding settlement; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: compare attacker donation cost to any increased redeemable value after price update Use probe condition: daily mint limit route; amount case 2 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.
