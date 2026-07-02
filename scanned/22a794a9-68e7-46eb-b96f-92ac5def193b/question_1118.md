# Q1118: receiveFromRewardReceiver Committed Assets Desync Price Update daily P1118

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromRewardReceiver()` while controlling msg.value and direct call ordering before updateRSETHPrice and create committed withdrawal assets then make total asset accounting move independently, causing `contracts/LRTDepositPool.sol::receiveFromRewardReceiver` to break the invariant that assetsCommitted never exceeds realistically available assets in a way that strands users; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver, leading to permanent freezing of unclaimed yield? Probe condition: daily fee mint limit route; amount case available liquidity minus 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromRewardReceiver
- Entrypoint: external payable receiveFromRewardReceiver()
- Attacker controls: msg.value and direct call ordering before updateRSETHPrice; scenario: create committed withdrawal assets then make total asset accounting move independently; validation style: two transactions before and after updateRSETHPrice; probe condition: daily fee mint limit route; amount case available liquidity minus 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller
- Exploit idea: Use two-step sequence to exercise the committed-assets desync path against receiveFromRewardReceiver and look for price update breaking value conservation or liveness.
- Invariant to test: assetsCommitted never exceeds realistically available assets in a way that strands users; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver
- Expected Immunefi impact: Medium. Permanent freezing of unclaimed yield
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: daily fee mint limit route; amount case available liquidity minus 1 wei; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.
