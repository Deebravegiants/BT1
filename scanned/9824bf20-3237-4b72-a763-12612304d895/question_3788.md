# Q3788: updateRSETHPrice Unexpected Receiver Revert Rounding LRTConverter P3788

## Question
Can an unprivileged public caller enter through `public updateRSETHPrice()` while controlling call timing after deposits, withdrawals, reward sends, donations, or external balance changes and use a receiver contract that rejects ETH or token callbacks during completion, causing `contracts/LRTOracle.sol::updateRSETHPrice` to break the invariant that one receiver cannot freeze protocol-wide funds or consume other users liquidity; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice, leading to failure to deliver promised returns without principal loss? Probe condition: LRTConverter ETH-in-withdrawal route; amount case 1 ether; timing immediately after direct ETH donation; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::updateRSETHPrice
- Entrypoint: public updateRSETHPrice()
- Attacker controls: call timing after deposits, withdrawals, reward sends, donations, or external balance changes; scenario: use a receiver contract that rejects ETH or token callbacks during completion; validation style: compare ETH, stETH, and ETHx branches under the same value; probe condition: LRTConverter ETH-in-withdrawal route; amount case 1 ether; timing immediately after direct ETH donation; caller model EOA caller
- Exploit idea: Use asset pair differential to exercise the unexpected receiver revert path against updateRSETHPrice and look for rounding breaking value conservation or liveness.
- Invariant to test: one receiver cannot freeze protocol-wide funds or consume other users liquidity; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: LRTConverter ETH-in-withdrawal route; amount case 1 ether; timing immediately after direct ETH donation; caller model EOA caller.
