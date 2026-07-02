# Q3619: updateRSETHPrice Highest Price Ratchet Rounding Lido P3619

## Question
Can an unprivileged public caller enter through `public updateRSETHPrice()` while controlling call timing after deposits, withdrawals, reward sends, donations, or external balance changes and cause highestRsethPrice to ratchet from donated or transient balances then later reverse, causing `contracts/LRTOracle.sol::updateRSETHPrice` to break the invariant that price protection cannot freeze funds or make withdrawals insolvent from transient TVL; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice, leading to temporary freezing of funds? Probe condition: Lido stETH unstake route; amount case 1 wei; timing immediately after direct ETH donation; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::updateRSETHPrice
- Entrypoint: public updateRSETHPrice()
- Attacker controls: call timing after deposits, withdrawals, reward sends, donations, or external balance changes; scenario: cause highestRsethPrice to ratchet from donated or transient balances then later reverse; validation style: an attacker contract as msg.sender or recipient; probe condition: Lido stETH unstake route; amount case 1 wei; timing immediately after direct ETH donation; caller model EOA caller
- Exploit idea: Use receiver contract path to exercise the highest-price ratchet path against updateRSETHPrice and look for rounding breaking value conservation or liveness.
- Invariant to test: price protection cannot freeze funds or make withdrawals insolvent from transient TVL; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: Lido stETH unstake route; amount case 1 wei; timing immediately after direct ETH donation; caller model EOA caller.
