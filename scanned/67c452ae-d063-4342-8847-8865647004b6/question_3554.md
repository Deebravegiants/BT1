# Q3554: updateRSETHPrice Pause Boundary Race Rounding deposit-limit P3554

## Question
Can an unprivileged public caller enter through `public updateRSETHPrice()` while controlling call timing after deposits, withdrawals, reward sends, donations, or external balance changes and race a public action around a pause or public price-triggered pause transition, causing `contracts/LRTOracle.sol::updateRSETHPrice` to break the invariant that paused state cannot leave assets burned, committed, or transferred without corresponding settlement; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice, leading to protocol insolvency? Probe condition: deposit-limit accounting route; amount case available liquidity plus 1 wei; timing immediately after reward sendFunds; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::updateRSETHPrice
- Entrypoint: public updateRSETHPrice()
- Attacker controls: call timing after deposits, withdrawals, reward sends, donations, or external balance changes; scenario: race a public action around a pause or public price-triggered pause transition; validation style: two transactions before and after updateRSETHPrice; probe condition: deposit-limit accounting route; amount case available liquidity plus 1 wei; timing immediately after reward sendFunds; caller model EOA caller
- Exploit idea: Use two-step sequence to exercise the pause boundary race path against updateRSETHPrice and look for rounding breaking value conservation or liveness.
- Invariant to test: paused state cannot leave assets burned, committed, or transferred without corresponding settlement; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: deposit-limit accounting route; amount case available liquidity plus 1 wei; timing immediately after reward sendFunds; caller model EOA caller.
