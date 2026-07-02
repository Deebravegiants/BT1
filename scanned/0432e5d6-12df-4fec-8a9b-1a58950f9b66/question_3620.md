# Q3620: updateRSETHPrice Highest Price Ratchet Price Update Swell P3620

## Question
Can an unprivileged public caller enter through `public updateRSETHPrice()` while controlling call timing after deposits, withdrawals, reward sends, donations, or external balance changes and cause highestRsethPrice to ratchet from donated or transient balances then later reverse, causing `contracts/LRTOracle.sol::updateRSETHPrice` to break the invariant that price protection cannot freeze funds or make withdrawals insolvent from transient TVL; specifically, price update must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice, leading to failure to deliver promised returns without principal loss? Probe condition: Swell swETH legacy route; amount case 1 wei; timing immediately after direct ETH donation; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::updateRSETHPrice
- Entrypoint: public updateRSETHPrice()
- Attacker controls: call timing after deposits, withdrawals, reward sends, donations, or external balance changes; scenario: cause highestRsethPrice to ratchet from donated or transient balances then later reverse; validation style: compare ETH, stETH, and ETHx branches under the same value; probe condition: Swell swETH legacy route; amount case 1 wei; timing immediately after direct ETH donation; caller model EOA caller
- Exploit idea: Use asset pair differential to exercise the highest-price ratchet path against updateRSETHPrice and look for price update breaking value conservation or liveness.
- Invariant to test: price protection cannot freeze funds or make withdrawals insolvent from transient TVL; specifically, price update must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: Swell swETH legacy route; amount case 1 wei; timing immediately after direct ETH donation; caller model EOA caller.
