# Q3596: updateRSETHPrice FirstExcludedIndex Boundary Highest Price queued P3596

## Question
Can an unprivileged public caller enter through `public updateRSETHPrice()` while controlling call timing after deposits, withdrawals, reward sends, donations, or external balance changes and fill withdrawal requests around the unlockQueue firstExcludedIndex boundary, causing `contracts/LRTOracle.sol::updateRSETHPrice` to break the invariant that unlocking cannot skip, over-unlock, or permanently strand requests; specifically, highest price must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice, leading to permanent freezing of unclaimed yield? Probe condition: queued buffer route; amount case deposit limit plus 1 wei; timing immediately after reward sendFunds; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::updateRSETHPrice
- Entrypoint: public updateRSETHPrice()
- Attacker controls: call timing after deposits, withdrawals, reward sends, donations, or external balance changes; scenario: fill withdrawal requests around the unlockQueue firstExcludedIndex boundary; validation style: compare ETH, stETH, and ETHx branches under the same value; probe condition: queued buffer route; amount case deposit limit plus 1 wei; timing immediately after reward sendFunds; caller model EOA caller
- Exploit idea: Use asset pair differential to exercise the firstExcludedIndex boundary path against updateRSETHPrice and look for highest price breaking value conservation or liveness.
- Invariant to test: unlocking cannot skip, over-unlock, or permanently strand requests; specifically, highest price must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice
- Expected Immunefi impact: Medium. Permanent freezing of unclaimed yield
- Fast validation: write a Foundry stateful test and assert protocol balances, liabilities, and user payouts remain conserved Use probe condition: queued buffer route; amount case deposit limit plus 1 wei; timing immediately after reward sendFunds; caller model EOA caller.
