# Q3479: updateRSETHPrice Round Down Accumulation Fee Mint Lido P3479

## Question
Can an unprivileged public caller enter through `public updateRSETHPrice()` while controlling call timing after deposits, withdrawals, reward sends, donations, or external balance changes and split a large action into many dust-sized calls to accumulate rounding residue in the attacker direction, causing `contracts/LRTOracle.sol::updateRSETHPrice` to break the invariant that sum of split outputs is not greater than one equivalent unsplit output; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice, leading to permanent freezing of unclaimed yield? Probe condition: Lido stETH unstake route; amount case daily limit minus 1 wei; timing immediately after reward sendFunds; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::updateRSETHPrice
- Entrypoint: public updateRSETHPrice()
- Attacker controls: call timing after deposits, withdrawals, reward sends, donations, or external balance changes; scenario: split a large action into many dust-sized calls to accumulate rounding residue in the attacker direction; validation style: a local supported-token harness with configurable transfer behavior; probe condition: Lido stETH unstake route; amount case daily limit minus 1 wei; timing immediately after reward sendFunds; caller model EOA caller
- Exploit idea: Use malicious ERC20 harness to exercise the round-down accumulation path against updateRSETHPrice and look for fee mint breaking value conservation or liveness.
- Invariant to test: sum of split outputs is not greater than one equivalent unsplit output; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice
- Expected Immunefi impact: Medium. Permanent freezing of unclaimed yield
- Fast validation: track protocol fee receiver, rsETH supply, and TVL before/after updateRSETHPrice across period boundaries Use probe condition: Lido stETH unstake route; amount case daily limit minus 1 wei; timing immediately after reward sendFunds; caller model EOA caller.
