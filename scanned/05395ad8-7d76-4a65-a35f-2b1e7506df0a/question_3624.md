# Q3624: updateRSETHPrice Highest Price Ratchet Rounding rsETH P3624

## Question
Can an unprivileged public caller enter through `public updateRSETHPrice()` while controlling call timing after deposits, withdrawals, reward sends, donations, or external balance changes and cause highestRsethPrice to ratchet from donated or transient balances then later reverse, causing `contracts/LRTOracle.sol::updateRSETHPrice` to break the invariant that price protection cannot freeze funds or make withdrawals insolvent from transient TVL; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice, leading to theft of unclaimed yield? Probe condition: rsETH burn route; amount case 2 wei; timing immediately after direct ETH donation; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::updateRSETHPrice
- Entrypoint: public updateRSETHPrice()
- Attacker controls: call timing after deposits, withdrawals, reward sends, donations, or external balance changes; scenario: cause highestRsethPrice to ratchet from donated or transient balances then later reverse; validation style: attacker-created state followed by an honest operator action; probe condition: rsETH burn route; amount case 2 wei; timing immediately after direct ETH donation; caller model EOA caller
- Exploit idea: Use operator-normalization follow-up to exercise the highest-price ratchet path against updateRSETHPrice and look for rounding breaking value conservation or liveness.
- Invariant to test: price protection cannot freeze funds or make withdrawals insolvent from transient TVL; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice
- Expected Immunefi impact: High. Theft of unclaimed yield
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: rsETH burn route; amount case 2 wei; timing immediately after direct ETH donation; caller model EOA caller.
