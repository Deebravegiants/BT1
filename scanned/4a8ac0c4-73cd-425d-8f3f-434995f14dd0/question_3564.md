# Q3564: updateRSETHPrice Pause Boundary Race Rounding rsETH P3564

## Question
Can an unprivileged public caller enter through `public updateRSETHPrice()` while controlling call timing after deposits, withdrawals, reward sends, donations, or external balance changes and race a public action around a pause or public price-triggered pause transition, causing `contracts/LRTOracle.sol::updateRSETHPrice` to break the invariant that paused state cannot leave assets burned, committed, or transferred without corresponding settlement; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice, leading to temporary freezing of funds? Probe condition: rsETH burn route; amount case deposit limit minus 1 wei; timing immediately after reward sendFunds; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::updateRSETHPrice
- Entrypoint: public updateRSETHPrice()
- Attacker controls: call timing after deposits, withdrawals, reward sends, donations, or external balance changes; scenario: race a public action around a pause or public price-triggered pause transition; validation style: attacker-created state followed by an honest operator action; probe condition: rsETH burn route; amount case deposit limit minus 1 wei; timing immediately after reward sendFunds; caller model EOA caller
- Exploit idea: Use operator-normalization follow-up to exercise the pause boundary race path against updateRSETHPrice and look for rounding breaking value conservation or liveness.
- Invariant to test: paused state cannot leave assets burned, committed, or transferred without corresponding settlement; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: rsETH burn route; amount case deposit limit minus 1 wei; timing immediately after reward sendFunds; caller model EOA caller.
