# Q3490: updateRSETHPrice Round Up Insolvency Fee Mint NodeDelegator P3490

## Question
Can an unprivileged public caller enter through `public updateRSETHPrice()` while controlling call timing after deposits, withdrawals, reward sends, donations, or external balance changes and choose amounts just above precision boundaries so liabilities round up while assets round down, causing `contracts/LRTOracle.sol::updateRSETHPrice` to break the invariant that rsETH liabilities never exceed normalized protocol assets; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice, leading to permanent freezing of unclaimed yield? Probe condition: NodeDelegator pod-share route; amount case daily limit exactly; timing immediately after reward sendFunds; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::updateRSETHPrice
- Entrypoint: public updateRSETHPrice()
- Attacker controls: call timing after deposits, withdrawals, reward sends, donations, or external balance changes; scenario: choose amounts just above precision boundaries so liabilities round up while assets round down; validation style: stateful fuzzing over deposit, update price, withdraw, unlock, complete; probe condition: NodeDelegator pod-share route; amount case daily limit exactly; timing immediately after reward sendFunds; caller model EOA caller
- Exploit idea: Use stateful invariant fuzz to exercise the round-up insolvency path against updateRSETHPrice and look for fee mint breaking value conservation or liveness.
- Invariant to test: rsETH liabilities never exceed normalized protocol assets; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice
- Expected Immunefi impact: Medium. Permanent freezing of unclaimed yield
- Fast validation: track protocol fee receiver, rsETH supply, and TVL before/after updateRSETHPrice across period boundaries Use probe condition: NodeDelegator pod-share route; amount case daily limit exactly; timing immediately after reward sendFunds; caller model EOA caller.
