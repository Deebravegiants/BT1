# Q3543: updateRSETHPrice Reentrant Token Callback Rounding ETHx P3543

## Question
Can an unprivileged public caller enter through `public updateRSETHPrice()` while controlling call timing after deposits, withdrawals, reward sends, donations, or external balance changes and use an ERC777-like or malicious token callback during safeTransferFrom/safeTransfer to reenter another public protocol path, causing `contracts/LRTOracle.sol::updateRSETHPrice` to break the invariant that nonReentrant and state ordering prevent double mint, double claim, or liquidity theft; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice, leading to protocol insolvency? Probe condition: ETHx supported asset route; amount case available liquidity plus 1 wei; timing immediately after reward sendFunds; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::updateRSETHPrice
- Entrypoint: public updateRSETHPrice()
- Attacker controls: call timing after deposits, withdrawals, reward sends, donations, or external balance changes; scenario: use an ERC777-like or malicious token callback during safeTransferFrom/safeTransfer to reenter another public protocol path; validation style: a helper contract batching allowed public calls; probe condition: ETHx supported asset route; amount case available liquidity plus 1 wei; timing immediately after reward sendFunds; caller model EOA caller
- Exploit idea: Use batched multicall-style sequence to exercise the reentrant token callback path against updateRSETHPrice and look for rounding breaking value conservation or liveness.
- Invariant to test: nonReentrant and state ordering prevent double mint, double claim, or liquidity theft; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: ETHx supported asset route; amount case available liquidity plus 1 wei; timing immediately after reward sendFunds; caller model EOA caller.
