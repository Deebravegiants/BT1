# Q3669: updateRSETHPrice Buffer Over Reservation Price Update LRTUnstakingVault P3669

## Question
Can an unprivileged public caller enter through `public updateRSETHPrice()` while controlling call timing after deposits, withdrawals, reward sends, donations, or external balance changes and create queued withdrawal state that makes buffer reserve more than actual liabilities, causing `contracts/LRTOracle.sol::updateRSETHPrice` to break the invariant that stale buffers cannot permanently freeze free liquidity; specifically, price update must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice, leading to permanent freezing of unclaimed yield? Probe condition: LRTUnstakingVault instant-liquidity route; amount case exact minAmount; timing immediately after direct ETH donation; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::updateRSETHPrice
- Entrypoint: public updateRSETHPrice()
- Attacker controls: call timing after deposits, withdrawals, reward sends, donations, or external balance changes; scenario: create queued withdrawal state that makes buffer reserve more than actual liabilities; validation style: warp/block-roll around day or withdrawal-delay boundaries; probe condition: LRTUnstakingVault instant-liquidity route; amount case exact minAmount; timing immediately after direct ETH donation; caller model EOA caller
- Exploit idea: Use period boundary fuzz to exercise the buffer over-reservation path against updateRSETHPrice and look for price update breaking value conservation or liveness.
- Invariant to test: stale buffers cannot permanently freeze free liquidity; specifically, price update must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice
- Expected Immunefi impact: Medium. Permanent freezing of unclaimed yield
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: LRTUnstakingVault instant-liquidity route; amount case exact minAmount; timing immediately after direct ETH donation; caller model EOA caller.
