# Q3615: updateRSETHPrice Highest Price Ratchet Price Update withdrawal P3615

## Question
Can an unprivileged public caller enter through `public updateRSETHPrice()` while controlling call timing after deposits, withdrawals, reward sends, donations, or external balance changes and cause highestRsethPrice to ratchet from donated or transient balances then later reverse, causing `contracts/LRTOracle.sol::updateRSETHPrice` to break the invariant that price protection cannot freeze funds or make withdrawals insolvent from transient TVL; specifically, price update must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice, leading to permanent freezing of funds? Probe condition: withdrawal request nonce route; amount case 1 wei; timing immediately after direct ETH donation; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::updateRSETHPrice
- Entrypoint: public updateRSETHPrice()
- Attacker controls: call timing after deposits, withdrawals, reward sends, donations, or external balance changes; scenario: cause highestRsethPrice to ratchet from donated or transient balances then later reverse; validation style: a helper contract batching allowed public calls; probe condition: withdrawal request nonce route; amount case 1 wei; timing immediately after direct ETH donation; caller model EOA caller
- Exploit idea: Use batched multicall-style sequence to exercise the highest-price ratchet path against updateRSETHPrice and look for price update breaking value conservation or liveness.
- Invariant to test: price protection cannot freeze funds or make withdrawals insolvent from transient TVL; specifically, price update must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice
- Expected Immunefi impact: Critical. Permanent freezing of funds
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: withdrawal request nonce route; amount case 1 wei; timing immediately after direct ETH donation; caller model EOA caller.
