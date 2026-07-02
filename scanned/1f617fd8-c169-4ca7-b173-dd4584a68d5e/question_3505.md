# Q3505: updateRSETHPrice Direct ETH Donation Skew Rounding rsETH P3505

## Question
Can an unprivileged public caller enter through `public updateRSETHPrice()` while controlling call timing after deposits, withdrawals, reward sends, donations, or external balance changes and send ETH directly to permissive receive-style functions before an accounting read, causing `contracts/LRTOracle.sol::updateRSETHPrice` to break the invariant that donated ETH cannot be converted into attacker-owned principal beyond the donated amount; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice, leading to permanent freezing of unclaimed yield? Probe condition: rsETH transfer route; amount case available liquidity minus 1 wei; timing immediately after reward sendFunds; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::updateRSETHPrice
- Entrypoint: public updateRSETHPrice()
- Attacker controls: call timing after deposits, withdrawals, reward sends, donations, or external balance changes; scenario: send ETH directly to permissive receive-style functions before an accounting read; validation style: one transaction using a contract wallet and controlled calldata; probe condition: rsETH transfer route; amount case available liquidity minus 1 wei; timing immediately after reward sendFunds; caller model EOA caller
- Exploit idea: Use single transaction to exercise the direct ETH donation skew path against updateRSETHPrice and look for rounding breaking value conservation or liveness.
- Invariant to test: donated ETH cannot be converted into attacker-owned principal beyond the donated amount; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice
- Expected Immunefi impact: Medium. Permanent freezing of unclaimed yield
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: rsETH transfer route; amount case available liquidity minus 1 wei; timing immediately after reward sendFunds; caller model EOA caller.
