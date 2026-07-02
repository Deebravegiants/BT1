# Q3810: updateRSETHPrice Committed Assets Desync Rounding NodeDelegator P3810

## Question
Can an unprivileged public caller enter through `public updateRSETHPrice()` while controlling call timing after deposits, withdrawals, reward sends, donations, or external balance changes and create committed withdrawal assets then make total asset accounting move independently, causing `contracts/LRTOracle.sol::updateRSETHPrice` to break the invariant that assetsCommitted never exceeds realistically available assets in a way that strands users; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice, leading to failure to deliver promised returns without principal loss? Probe condition: NodeDelegator pod-share route; amount case 31.999999 ether; timing immediately after direct ETH donation; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::updateRSETHPrice
- Entrypoint: public updateRSETHPrice()
- Attacker controls: call timing after deposits, withdrawals, reward sends, donations, or external balance changes; scenario: create committed withdrawal assets then make total asset accounting move independently; validation style: compare many dust calls against one large call; probe condition: NodeDelegator pod-share route; amount case 31.999999 ether; timing immediately after direct ETH donation; caller model EOA caller
- Exploit idea: Use dust-to-large differential to exercise the committed-assets desync path against updateRSETHPrice and look for rounding breaking value conservation or liveness.
- Invariant to test: assetsCommitted never exceeds realistically available assets in a way that strands users; specifically, rounding must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: differential-test split versus unsplit amounts and assert no attacker-positive value drift Use probe condition: NodeDelegator pod-share route; amount case 31.999999 ether; timing immediately after direct ETH donation; caller model EOA caller.
