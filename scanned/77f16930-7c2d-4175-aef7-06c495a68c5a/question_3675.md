# Q3675: updateRSETHPrice Claim Replay Price Update withdrawal P3675

## Question
Can an unprivileged public caller enter through `public updateRSETHPrice()` while controlling call timing after deposits, withdrawals, reward sends, donations, or external balance changes and repeat a claim, completion, or callback after state deletion or transfer occurs, causing `contracts/LRTOracle.sol::updateRSETHPrice` to break the invariant that one claim/request/NFT/token id settles at most once; specifically, price update must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice, leading to failure to deliver promised returns without principal loss? Probe condition: withdrawal request nonce route; amount case exact minAmount; timing immediately after direct ETH donation; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::updateRSETHPrice
- Entrypoint: public updateRSETHPrice()
- Attacker controls: call timing after deposits, withdrawals, reward sends, donations, or external balance changes; scenario: repeat a claim, completion, or callback after state deletion or transfer occurs; validation style: a helper contract batching allowed public calls; probe condition: withdrawal request nonce route; amount case exact minAmount; timing immediately after direct ETH donation; caller model EOA caller
- Exploit idea: Use batched multicall-style sequence to exercise the claim replay path against updateRSETHPrice and look for price update breaking value conservation or liveness.
- Invariant to test: one claim/request/NFT/token id settles at most once; specifically, price update must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: withdrawal request nonce route; amount case exact minAmount; timing immediately after direct ETH donation; caller model EOA caller.
