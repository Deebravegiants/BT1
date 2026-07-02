# Q3783: updateRSETHPrice Unexpected Receiver Revert Rounding ETHx P3783

## Question
Can an unprivileged public caller enter through `public updateRSETHPrice()` while controlling call timing after deposits, withdrawals, reward sends, donations, or external balance changes and use a receiver contract that rejects ETH or token callbacks during completion, causing `contracts/LRTOracle.sol::updateRSETHPrice` to break the invariant that one receiver cannot freeze protocol-wide funds or consume other users liquidity; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice, leading to permanent freezing of funds? Probe condition: ETHx supported asset route; amount case 1 ether; timing immediately after direct ETH donation; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::updateRSETHPrice
- Entrypoint: public updateRSETHPrice()
- Attacker controls: call timing after deposits, withdrawals, reward sends, donations, or external balance changes; scenario: use a receiver contract that rejects ETH or token callbacks during completion; validation style: a helper contract batching allowed public calls; probe condition: ETHx supported asset route; amount case 1 ether; timing immediately after direct ETH donation; caller model EOA caller
- Exploit idea: Use batched multicall-style sequence to exercise the unexpected receiver revert path against updateRSETHPrice and look for rounding breaking value conservation or liveness.
- Invariant to test: one receiver cannot freeze protocol-wide funds or consume other users liquidity; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: ETHx supported asset route; amount case 1 ether; timing immediately after direct ETH donation; caller model EOA caller.
