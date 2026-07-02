# Q3806: updateRSETHPrice Committed Assets Desync Price Update LRTOracle P3806

## Question
Can an unprivileged public caller enter through `public updateRSETHPrice()` while controlling call timing after deposits, withdrawals, reward sends, donations, or external balance changes and create committed withdrawal assets then make total asset accounting move independently, causing `contracts/LRTOracle.sol::updateRSETHPrice` to break the invariant that assetsCommitted never exceeds realistically available assets in a way that strands users; specifically, price update must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice, leading to protocol insolvency? Probe condition: LRTOracle price route; amount case 31.999999 ether; timing immediately after direct ETH donation; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::updateRSETHPrice
- Entrypoint: public updateRSETHPrice()
- Attacker controls: call timing after deposits, withdrawals, reward sends, donations, or external balance changes; scenario: create committed withdrawal assets then make total asset accounting move independently; validation style: two transactions before and after updateRSETHPrice; probe condition: LRTOracle price route; amount case 31.999999 ether; timing immediately after direct ETH donation; caller model EOA caller
- Exploit idea: Use two-step sequence to exercise the committed-assets desync path against updateRSETHPrice and look for price update breaking value conservation or liveness.
- Invariant to test: assetsCommitted never exceeds realistically available assets in a way that strands users; specifically, price update must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice
- Expected Immunefi impact: Critical. Protocol insolvency
- Fast validation: statefully call public updateRSETHPrice after each balance-changing action and assert backing invariants Use probe condition: LRTOracle price route; amount case 31.999999 ether; timing immediately after direct ETH donation; caller model EOA caller.
