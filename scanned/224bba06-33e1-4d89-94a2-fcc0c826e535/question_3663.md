# Q3663: updateRSETHPrice Buffer Over Reservation Rounding ETHx P3663

## Question
Can an unprivileged public caller enter through `public updateRSETHPrice()` while controlling call timing after deposits, withdrawals, reward sends, donations, or external balance changes and create queued withdrawal state that makes buffer reserve more than actual liabilities, causing `contracts/LRTOracle.sol::updateRSETHPrice` to break the invariant that stale buffers cannot permanently freeze free liquidity; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice, leading to temporary freezing of funds? Probe condition: ETHx supported asset route; amount case exact minAmount; timing immediately after direct ETH donation; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::updateRSETHPrice
- Entrypoint: public updateRSETHPrice()
- Attacker controls: call timing after deposits, withdrawals, reward sends, donations, or external balance changes; scenario: create queued withdrawal state that makes buffer reserve more than actual liabilities; validation style: a helper contract batching allowed public calls; probe condition: ETHx supported asset route; amount case exact minAmount; timing immediately after direct ETH donation; caller model EOA caller
- Exploit idea: Use batched multicall-style sequence to exercise the buffer over-reservation path against updateRSETHPrice and look for rounding breaking value conservation or liveness.
- Invariant to test: stale buffers cannot permanently freeze free liquidity; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: ETHx supported asset route; amount case exact minAmount; timing immediately after direct ETH donation; caller model EOA caller.
