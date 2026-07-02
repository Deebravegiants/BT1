# Q1508: receiveFromLRTConverter Committed Assets Desync Donation Accounting LRTConverter P1508

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromLRTConverter()` while controlling msg.value and call ordering relative to ethValueInWithdrawal and create committed withdrawal assets then make total asset accounting move independently, causing `contracts/LRTDepositPool.sol::receiveFromLRTConverter` to break the invariant that assetsCommitted never exceeds realistically available assets in a way that strands users; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for receiveFromLRTConverter, leading to permanent freezing of funds? Probe condition: LRTConverter ETH-in-withdrawal route; amount case available liquidity minus 1 wei; timing at withdrawalDelayBlocks exactly; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromLRTConverter
- Entrypoint: external payable receiveFromLRTConverter()
- Attacker controls: msg.value and call ordering relative to ethValueInWithdrawal; scenario: create committed withdrawal assets then make total asset accounting move independently; validation style: compare ETH, stETH, and ETHx branches under the same value; probe condition: LRTConverter ETH-in-withdrawal route; amount case available liquidity minus 1 wei; timing at withdrawalDelayBlocks exactly; caller model EOA caller
- Exploit idea: Use asset pair differential to exercise the committed-assets desync path against receiveFromLRTConverter and look for donation accounting breaking value conservation or liveness.
- Invariant to test: assetsCommitted never exceeds realistically available assets in a way that strands users; specifically, donation accounting must not violate backing, queue, yield, or liquidity accounting for receiveFromLRTConverter
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: compare attacker donation cost to any increased redeemable value after price update Use probe condition: LRTConverter ETH-in-withdrawal route; amount case available liquidity minus 1 wei; timing at withdrawalDelayBlocks exactly; caller model EOA caller.
