# Q1059: receiveFromRewardReceiver Allowance Race Price Update Lido P1059

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromRewardReceiver()` while controlling msg.value and direct call ordering before updateRSETHPrice and change ERC20 allowance/balance between calculation and transfer using supported token behavior, causing `contracts/LRTDepositPool.sol::receiveFromRewardReceiver` to break the invariant that protocol mints/burns only after actual spendable value is secured; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver, leading to permanent freezing of unclaimed yield? Probe condition: Lido stETH unstake route; amount case 32.000001 ether; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromRewardReceiver
- Entrypoint: external payable receiveFromRewardReceiver()
- Attacker controls: msg.value and direct call ordering before updateRSETHPrice; scenario: change ERC20 allowance/balance between calculation and transfer using supported token behavior; validation style: a helper contract batching allowed public calls; probe condition: Lido stETH unstake route; amount case 32.000001 ether; timing at withdrawalDelayBlocks minus 1; caller model EOA caller
- Exploit idea: Use batched multicall-style sequence to exercise the allowance race path against receiveFromRewardReceiver and look for price update breaking value conservation or liveness.
- Invariant to test: protocol mints/burns only after actual spendable value is secured; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver
- Expected Immunefi impact: Medium. Permanent freezing of unclaimed yield
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: Lido stETH unstake route; amount case 32.000001 ether; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.
