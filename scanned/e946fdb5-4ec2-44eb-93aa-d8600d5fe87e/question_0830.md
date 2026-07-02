# Q830: receiveFromRewardReceiver Fee On Transfer Token Skew Price Update NodeDelegator P0830

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromRewardReceiver()` while controlling msg.value and direct call ordering before updateRSETHPrice and use a supported ERC20 path where received balance is lower than depositAmount or transfer amount, causing `contracts/LRTDepositPool.sol::receiveFromRewardReceiver` to break the invariant that minted rsETH and committed withdrawals are based on actual assets received; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver, leading to permanent freezing of unclaimed yield? Probe condition: NodeDelegator pod-share route; amount case 2 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromRewardReceiver
- Entrypoint: external payable receiveFromRewardReceiver()
- Attacker controls: msg.value and direct call ordering before updateRSETHPrice; scenario: use a supported ERC20 path where received balance is lower than depositAmount or transfer amount; validation style: two transactions before and after updateRSETHPrice; probe condition: NodeDelegator pod-share route; amount case 2 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller
- Exploit idea: Use two-step sequence to exercise the fee-on-transfer token skew path against receiveFromRewardReceiver and look for price update breaking value conservation or liveness.
- Invariant to test: minted rsETH and committed withdrawals are based on actual assets received; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver
- Expected Immunefi impact: Medium. Permanent freezing of unclaimed yield
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: NodeDelegator pod-share route; amount case 2 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.
