# Q3625: updateRSETHPrice Fee Mint Limit Boundary Rounding rsETH P3625

## Question
Can an unprivileged public caller enter through `public updateRSETHPrice()` while controlling call timing after deposits, withdrawals, reward sends, donations, or external balance changes and execute price updates at exactly fee-period or mint-period boundaries, causing `contracts/LRTOracle.sol::updateRSETHPrice` to break the invariant that daily limits cannot be bypassed or permanently block legitimate minting; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice, leading to direct theft of user funds? Probe condition: rsETH transfer route; amount case 2 wei; timing immediately after direct ETH donation; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::updateRSETHPrice
- Entrypoint: public updateRSETHPrice()
- Attacker controls: call timing after deposits, withdrawals, reward sends, donations, or external balance changes; scenario: execute price updates at exactly fee-period or mint-period boundaries; validation style: one transaction using a contract wallet and controlled calldata; probe condition: rsETH transfer route; amount case 2 wei; timing immediately after direct ETH donation; caller model EOA caller
- Exploit idea: Use single transaction to exercise the fee mint limit boundary path against updateRSETHPrice and look for rounding breaking value conservation or liveness.
- Invariant to test: daily limits cannot be bypassed or permanently block legitimate minting; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice
- Expected Immunefi impact: Critical. Direct theft of any user funds, whether at-rest or in-motion, other than unclaimed yield
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: rsETH transfer route; amount case 2 wei; timing immediately after direct ETH donation; caller model EOA caller.
