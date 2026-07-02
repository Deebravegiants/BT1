# Q3563: updateRSETHPrice Pause Boundary Race Highest Price ETHx P3563

## Question
Can an unprivileged public caller enter through `public updateRSETHPrice()` while controlling call timing after deposits, withdrawals, reward sends, donations, or external balance changes and race a public action around a pause or public price-triggered pause transition, causing `contracts/LRTOracle.sol::updateRSETHPrice` to break the invariant that paused state cannot leave assets burned, committed, or transferred without corresponding settlement; specifically, highest price must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice, leading to permanent freezing of unclaimed yield? Probe condition: ETHx supported asset route; amount case deposit limit minus 1 wei; timing immediately after reward sendFunds; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::updateRSETHPrice
- Entrypoint: public updateRSETHPrice()
- Attacker controls: call timing after deposits, withdrawals, reward sends, donations, or external balance changes; scenario: race a public action around a pause or public price-triggered pause transition; validation style: a local supported-token harness with configurable transfer behavior; probe condition: ETHx supported asset route; amount case deposit limit minus 1 wei; timing immediately after reward sendFunds; caller model EOA caller
- Exploit idea: Use malicious ERC20 harness to exercise the pause boundary race path against updateRSETHPrice and look for highest price breaking value conservation or liveness.
- Invariant to test: paused state cannot leave assets burned, committed, or transferred without corresponding settlement; specifically, highest price must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice
- Expected Immunefi impact: Medium. Permanent freezing of unclaimed yield
- Fast validation: write a Foundry stateful test and assert protocol balances, liabilities, and user payouts remain conserved Use probe condition: ETHx supported asset route; amount case deposit limit minus 1 wei; timing immediately after reward sendFunds; caller model EOA caller.
