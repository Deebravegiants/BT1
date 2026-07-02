# Q3759: updateRSETHPrice Cross Contract Stale Read Pause Race Lido P3759

## Question
Can an unprivileged public caller enter through `public updateRSETHPrice()` while controlling call timing after deposits, withdrawals, reward sends, donations, or external balance changes and make one contract read another contract before its state reflects a prior step in the same attack sequence, causing `contracts/LRTOracle.sol::updateRSETHPrice` to break the invariant that cross-contract accounting snapshots cannot be inconsistent enough to steal or freeze funds; specifically, pause race must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice, leading to failure to deliver promised returns without principal loss? Probe condition: Lido stETH unstake route; amount case 0.01 ether; timing immediately after direct ETH donation; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::updateRSETHPrice
- Entrypoint: public updateRSETHPrice()
- Attacker controls: call timing after deposits, withdrawals, reward sends, donations, or external balance changes; scenario: make one contract read another contract before its state reflects a prior step in the same attack sequence; validation style: a helper contract batching allowed public calls; probe condition: Lido stETH unstake route; amount case 0.01 ether; timing immediately after direct ETH donation; caller model EOA caller
- Exploit idea: Use batched multicall-style sequence to exercise the cross-contract stale read path against updateRSETHPrice and look for pause race breaking value conservation or liveness.
- Invariant to test: cross-contract accounting snapshots cannot be inconsistent enough to steal or freeze funds; specifically, pause race must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: roll state around pause/updateRSETHPrice and assert no burned/committed assets remain unpaid Use probe condition: Lido stETH unstake route; amount case 0.01 ether; timing immediately after direct ETH donation; caller model EOA caller.
