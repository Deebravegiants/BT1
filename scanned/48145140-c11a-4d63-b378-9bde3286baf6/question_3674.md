# Q3674: updateRSETHPrice Claim Replay Rounding deposit-limit P3674

## Question
Can an unprivileged public caller enter through `public updateRSETHPrice()` while controlling call timing after deposits, withdrawals, reward sends, donations, or external balance changes and repeat a claim, completion, or callback after state deletion or transfer occurs, causing `contracts/LRTOracle.sol::updateRSETHPrice` to break the invariant that one claim/request/NFT/token id settles at most once; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice, leading to temporary freezing of funds? Probe condition: deposit-limit accounting route; amount case exact minAmount; timing immediately after direct ETH donation; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::updateRSETHPrice
- Entrypoint: public updateRSETHPrice()
- Attacker controls: call timing after deposits, withdrawals, reward sends, donations, or external balance changes; scenario: repeat a claim, completion, or callback after state deletion or transfer occurs; validation style: two transactions before and after updateRSETHPrice; probe condition: deposit-limit accounting route; amount case exact minAmount; timing immediately after direct ETH donation; caller model EOA caller
- Exploit idea: Use two-step sequence to exercise the claim replay path against updateRSETHPrice and look for rounding breaking value conservation or liveness.
- Invariant to test: one claim/request/NFT/token id settles at most once; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice
- Expected Immunefi impact: Medium. Temporary freezing of funds
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: deposit-limit accounting route; amount case exact minAmount; timing immediately after direct ETH donation; caller model EOA caller.
