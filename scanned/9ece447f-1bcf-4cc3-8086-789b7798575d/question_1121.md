# Q1121: receiveFromRewardReceiver Committed Assets Desync Fee Mint ETH P1121

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromRewardReceiver()` while controlling msg.value and direct call ordering before updateRSETHPrice and create committed withdrawal assets then make total asset accounting move independently, causing `contracts/LRTDepositPool.sol::receiveFromRewardReceiver` to break the invariant that assetsCommitted never exceeds realistically available assets in a way that strands users; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver, leading to theft of unclaimed yield? Probe condition: ETH sentinel route; amount case available liquidity exactly; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromRewardReceiver
- Entrypoint: external payable receiveFromRewardReceiver()
- Attacker controls: msg.value and direct call ordering before updateRSETHPrice; scenario: create committed withdrawal assets then make total asset accounting move independently; validation style: several attacker accounts creating adjacent requests; probe condition: ETH sentinel route; amount case available liquidity exactly; timing at withdrawalDelayBlocks minus 1; caller model EOA caller
- Exploit idea: Use multi-account queue pressure to exercise the committed-assets desync path against receiveFromRewardReceiver and look for fee mint breaking value conservation or liveness.
- Invariant to test: assetsCommitted never exceeds realistically available assets in a way that strands users; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for receiveFromRewardReceiver
- Expected Immunefi impact: High. Theft of unclaimed yield
- Fast validation: track protocol fee receiver, rsETH supply, and TVL before/after updateRSETHPrice across period boundaries Use probe condition: ETH sentinel route; amount case available liquidity exactly; timing at withdrawalDelayBlocks minus 1; caller model EOA caller.
