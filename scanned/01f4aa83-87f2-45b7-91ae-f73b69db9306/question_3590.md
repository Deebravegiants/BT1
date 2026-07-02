# Q3590: updateRSETHPrice FirstExcludedIndex Boundary Pause Race NodeDelegator P3590

## Question
Can an unprivileged public caller enter through `public updateRSETHPrice()` while controlling call timing after deposits, withdrawals, reward sends, donations, or external balance changes and fill withdrawal requests around the unlockQueue firstExcludedIndex boundary, causing `contracts/LRTOracle.sol::updateRSETHPrice` to break the invariant that unlocking cannot skip, over-unlock, or permanently strand requests; specifically, pause race must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice, leading to temporary freezing of funds? Probe condition: NodeDelegator pod-share route; amount case deposit limit plus 1 wei; timing immediately after reward sendFunds; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::updateRSETHPrice
- Entrypoint: public updateRSETHPrice()
- Attacker controls: call timing after deposits, withdrawals, reward sends, donations, or external balance changes; scenario: fill withdrawal requests around the unlockQueue firstExcludedIndex boundary; validation style: two transactions before and after updateRSETHPrice; probe condition: NodeDelegator pod-share route; amount case deposit limit plus 1 wei; timing immediately after reward sendFunds; caller model EOA caller
- Exploit idea: Use two-step sequence to exercise the firstExcludedIndex boundary path against updateRSETHPrice and look for pause race breaking value conservation or liveness.
- Invariant to test: unlocking cannot skip, over-unlock, or permanently strand requests; specifically, pause race must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: roll state around pause/updateRSETHPrice and assert no burned/committed assets remain unpaid Use probe condition: NodeDelegator pod-share route; amount case deposit limit plus 1 wei; timing immediately after reward sendFunds; caller model EOA caller.
