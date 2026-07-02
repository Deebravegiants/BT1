# Q3471: updateRSETHPrice Round Down Accumulation Highest Price EigenLayer P3471

## Question
Can an unprivileged public caller enter through `public updateRSETHPrice()` while controlling call timing after deposits, withdrawals, reward sends, donations, or external balance changes and split a large action into many dust-sized calls to accumulate rounding residue in the attacker direction, causing `contracts/LRTOracle.sol::updateRSETHPrice` to break the invariant that sum of split outputs is not greater than one equivalent unsplit output; specifically, highest price must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice, leading to theft of unclaimed yield? Probe condition: EigenLayer queued-withdrawal route; amount case daily limit minus 1 wei; timing immediately after reward sendFunds; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::updateRSETHPrice
- Entrypoint: public updateRSETHPrice()
- Attacker controls: call timing after deposits, withdrawals, reward sends, donations, or external balance changes; scenario: split a large action into many dust-sized calls to accumulate rounding residue in the attacker direction; validation style: a helper contract batching allowed public calls; probe condition: EigenLayer queued-withdrawal route; amount case daily limit minus 1 wei; timing immediately after reward sendFunds; caller model EOA caller
- Exploit idea: Use batched multicall-style sequence to exercise the round-down accumulation path against updateRSETHPrice and look for highest price breaking value conservation or liveness.
- Invariant to test: sum of split outputs is not greater than one equivalent unsplit output; specifically, highest price must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice
- Expected Immunefi impact: High. Theft of unclaimed yield
- Fast validation: write a Foundry stateful test and assert protocol balances, liabilities, and user payouts remain conserved Use probe condition: EigenLayer queued-withdrawal route; amount case daily limit minus 1 wei; timing immediately after reward sendFunds; caller model EOA caller.
