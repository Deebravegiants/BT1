# Q801: receiveFromRewardReceiver Round Up Insolvency Price Update ETH P0801

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromRewardReceiver()` while controlling msg.value and direct call ordering before updateRSETHPrice and choose amounts just above precision boundaries so liabilities round up while assets round down, causing `contracts/LRTDepositPool.sol::receiveFromRewardReceiver` to break the invariant that rsETH liabilities never exceed normalized protocol assets; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver, leading to permanent freezing of unclaimed yield? Probe condition: ETH sentinel route; amount case 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromRewardReceiver
- Entrypoint: external payable receiveFromRewardReceiver()
- Attacker controls: msg.value and direct call ordering before updateRSETHPrice; scenario: choose amounts just above precision boundaries so liabilities round up while assets round down; validation style: warp/block-roll around day or withdrawal-delay boundaries; probe condition: ETH sentinel route; amount case 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller
- Exploit idea: Use period boundary fuzz to exercise the round-up insolvency path against receiveFromRewardReceiver and look for price update breaking value conservation or liveness.
- Invariant to test: rsETH liabilities never exceed normalized protocol assets; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver
- Expected Immunefi impact: Medium. Permanent freezing of unclaimed yield
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: ETH sentinel route; amount case 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.
