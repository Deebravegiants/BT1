# Q941: receiveFromRewardReceiver Fee Mint Limit Boundary Price Update ETH P0941

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromRewardReceiver()` while controlling msg.value and direct call ordering before updateRSETHPrice and execute price updates at exactly fee-period or mint-period boundaries, causing `contracts/LRTDepositPool.sol::receiveFromRewardReceiver` to break the invariant that daily limits cannot be bypassed or permanently block legitimate minting; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver, leading to permanent freezing of unclaimed yield? Probe condition: ETH sentinel route; amount case 0.01 ether; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromRewardReceiver
- Entrypoint: external payable receiveFromRewardReceiver()
- Attacker controls: msg.value and direct call ordering before updateRSETHPrice; scenario: execute price updates at exactly fee-period or mint-period boundaries; validation style: several attacker accounts creating adjacent requests; probe condition: ETH sentinel route; amount case 0.01 ether; timing at withdrawalDelayBlocks minus 1; caller model EOA caller
- Exploit idea: Use multi-account queue pressure to exercise the fee mint limit boundary path against receiveFromRewardReceiver and look for price update breaking value conservation or liveness.
- Invariant to test: daily limits cannot be bypassed or permanently block legitimate minting; specifically, price update must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver
- Expected Immunefi impact: Medium. Permanent freezing of unclaimed yield
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: ETH sentinel route; amount case 0.01 ether; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.
