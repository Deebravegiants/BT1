# Q3807: updateRSETHPrice Committed Assets Desync Fee Mint FeeReceiver P3807

## Question
Can an unprivileged public caller enter through `public updateRSETHPrice()` while controlling call timing after deposits, withdrawals, reward sends, donations, or external balance changes and create committed withdrawal assets then make total asset accounting move independently, causing `contracts/LRTOracle.sol::updateRSETHPrice` to break the invariant that assetsCommitted never exceeds realistically available assets in a way that strands users; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice, leading to theft of unclaimed yield? Probe condition: FeeReceiver reward route; amount case 31.999999 ether; timing immediately after direct ETH donation; caller model EOA caller.

## Target
- File/function: contracts/LRTOracle.sol::updateRSETHPrice
- Entrypoint: public updateRSETHPrice()
- Attacker controls: call timing after deposits, withdrawals, reward sends, donations, or external balance changes; scenario: create committed withdrawal assets then make total asset accounting move independently; validation style: a helper contract batching allowed public calls; probe condition: FeeReceiver reward route; amount case 31.999999 ether; timing immediately after direct ETH donation; caller model EOA caller
- Exploit idea: Use batched multicall-style sequence to exercise the committed-assets desync path against updateRSETHPrice and look for fee mint breaking value conservation or liveness.
- Invariant to test: assetsCommitted never exceeds realistically available assets in a way that strands users; specifically, fee mint must not violate backing, queue, yield, or liquidity accounting for updateRSETHPrice
- Expected Immunefi impact: High. Theft of unclaimed yield
- Fast validation: track protocol fee receiver, rsETH supply, and TVL before/after updateRSETHPrice across period boundaries Use probe condition: FeeReceiver reward route; amount case 31.999999 ether; timing immediately after direct ETH donation; caller model EOA caller.
