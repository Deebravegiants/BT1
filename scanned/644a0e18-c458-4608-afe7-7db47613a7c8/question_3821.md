# Q3821: updateRSETHPrice Unclaimed Yield Diversion Rounding ETH P3821

## Question
Can an unprivileged public caller enter through `public updateRSETHPrice()` while controlling call timing after deposits, withdrawals, reward sends, donations, or external balance changes and time reward send, interest collection, fee minting, or claim settlement to redirect yield, causing `contracts/LRTOracle.sol::updateRSETHPrice` to break the invariant that unclaimed yield cannot be stolen or permanently frozen by a public caller; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice, leading to failure to deliver promised returns without principal loss? Probe condition: ETH sentinel route; amount case 32 ether; timing immediately after direct ETH donation; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::updateRSETHPrice
- Entrypoint: public updateRSETHPrice()
- Attacker controls: call timing after deposits, withdrawals, reward sends, donations, or external balance changes; scenario: time reward send, interest collection, fee minting, or claim settlement to redirect yield; validation style: several attacker accounts creating adjacent requests; probe condition: ETH sentinel route; amount case 32 ether; timing immediately after direct ETH donation; caller model EOA caller
- Exploit idea: Use multi-account queue pressure to exercise the unclaimed-yield diversion path against updateRSETHPrice and look for rounding breaking value conservation or liveness.
- Invariant to test: unclaimed yield cannot be stolen or permanently frozen by a public caller; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: ETH sentinel route; amount case 32 ether; timing immediately after direct ETH donation; caller model EOA caller.
