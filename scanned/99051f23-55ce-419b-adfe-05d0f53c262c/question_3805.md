# Q3805: updateRSETHPrice Committed Assets Desync Rounding rsETH P3805

## Question
Can an unprivileged public caller enter through `public updateRSETHPrice()` while controlling call timing after deposits, withdrawals, reward sends, donations, or external balance changes and create committed withdrawal assets then make total asset accounting move independently, causing `contracts/LRTOracle.sol::updateRSETHPrice` to break the invariant that assetsCommitted never exceeds realistically available assets in a way that strands users; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice, leading to permanent freezing of funds? Probe condition: rsETH transfer route; amount case 31.999999 ether; timing immediately after direct ETH donation; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::updateRSETHPrice
- Entrypoint: public updateRSETHPrice()
- Attacker controls: call timing after deposits, withdrawals, reward sends, donations, or external balance changes; scenario: create committed withdrawal assets then make total asset accounting move independently; validation style: one transaction using a contract wallet and controlled calldata; probe condition: rsETH transfer route; amount case 31.999999 ether; timing immediately after direct ETH donation; caller model EOA caller
- Exploit idea: Use single transaction to exercise the committed-assets desync path against updateRSETHPrice and look for rounding breaking value conservation or liveness.
- Invariant to test: assetsCommitted never exceeds realistically available assets in a way that strands users; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: rsETH transfer route; amount case 31.999999 ether; timing immediately after direct ETH donation; caller model EOA caller.
